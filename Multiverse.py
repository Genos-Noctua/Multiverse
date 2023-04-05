# Multiverse version 7.3
import hashlib, time, os.path, shutil, tarfile, queue, os
from pystray import Icon, Menu as menu, MenuItem as item
from tkinter.filedialog import *
from Assembler import *
from PIL import Image
import tkinter as tk

Service = 'C:\\Multiverse service\\'
paused = False
icon = True

class Entry:
    def compress(self):
        tail, head = os.path.split(self.file)
        archive = tarfile.open(Service + head + '.txz', 'w:xz')
        shutil.copyfile(self.file, Service + 'temp\\' + str(self.depth) + '-' + head)
        lol = [f for f in os.listdir(Service + 'temp\\') if os.path.isfile(os.path.join(Service + 'temp\\', f))]
        for name in lol:
            archive.add(Service + 'temp\\' + name, name)
        archive.close()
        shutil.rmtree(Service + 'temp', True)
    
    def decompress(self):
        tail, head = os.path.split(self.file)
        archive = tarfile.open(Service + head + '.txz', 'r:*')
        archive.extractall(Service + 'temp\\')
        archive.close()

    def save(self):
        tail, head = os.path.split(self.file)
        if os.path.isfile(Service + head + '.txz'):
            if os.path.isdir(Service + 'temp\\'): shutil.rmtree(Service + 'temp', True)
            self.decompress()
        else:
            os.mkdir(Service + 'temp\\')
        self.compress()
        self.depth += 1

    def where(self):
        tail, head = os.path.split(self.file)
        if not os.path.isdir(Service):
            os.mkdir(Service)
        if os.path.isfile(Service + head + '.txz'):
            self.decompress()
            temps = [f for f in os.listdir(Service + 'temp\\') if os.path.isfile(Service + 'temp\\' + f)]
            self.depth = len(temps)
            shutil.rmtree(Service + 'temp', True)

    def hash(self):
        with open(self.file, "rb") as f:
            data = f.read()
            hash_object = hashlib.sha256(data)
            self.sum = hash_object.hexdigest()

    def __init__(self):
        self.prev = 0
        self.sum = 0
        self.file = ""
        self.depth = 0

def on_clicked():
    window = tk.Tk()
    window.title('Edit File')

    text_box = tk.Text(window, height=20, width=50, font="Consolas 14")
    text_box.pack(expand=True, fill='both')

    with open('Files.txt', 'r') as file:
        text_box.insert('end', file.read())

    def save_changes():
        with open('Files.txt', 'w') as file:
            file.write(text_box.get('1.0', 'end-1c'))

    def open_files():
        files = askopenfilenames()
        for x in files[:-1]:
            text_box.insert('end', (x + "\n"))
        text_box.insert('end', files[-1])
        pass

    save_button = tk.Button(window, text='Save Changes', command=save_changes)
    save_button.pack()
    open_button = tk.Button(window, text='Open', command=open_files)
    open_button.pack()
    window.mainloop()

def Importer(node):
    newlist = node.input.get()
    if not os.path.isfile('Files.txt'):
        file = open('Files.txt', 'w+')
        file.close()
    with open('Files.txt', 'r') as file:
        string = file.read()
    if string == '':
        node.output.put(list())
        return
    files = str.split(string, sep='\n')
    temps = list()
    for x in newlist:
        if x.file in files:
            temps.append(x)
            files.remove(x.file)
    for x in files:
        entry = Entry()
        entry.file = x
        entry.where()
        entry.hash()
        entry.prev = entry.sum
        temps.append(entry) 
    node.output.put(temps)

def Processor(node):
    files = node.input.get()
    for x in files:
        x.hash()
        if x.prev != x.sum:
            x.prev = x.sum
            x.save()
    node.output.put(files)

def onn():
    global paused
    global icon
    paused = False
    f = open('active', 'w+')
    print('active', file=f, end='', flush=True)
    f.close()
    with Image.open('Running.ico') as f:
        icon.icon = f

def off():
    global paused
    global icon
    paused = True
    f = open('active', 'w+')
    print('inactive', file=f, end='', flush=True)
    f.close()
    with Image.open('Sleeping.ico') as f:
        icon.icon = f

def main():
    global paused
    global icon

    if not os.path.isfile('active'):
        open('active', 'w+').close()
        
    with open('active', 'r') as file:
        string = file.read()
        
        with Image.open("Running.ico") as f:
            icon = Icon('Multiverse', f, menu=menu(
                item('', on_clicked, visible=False, default=True),
                item('On', onn),
                item('Off', off)))
            
        if string == 'inactive':
            paused = True
            off()
        else:
            onn()
            
        icon.run_detached()

    entries = list()
    importer = Assembler(queue.Queue(0), queue.Queue(0), Importer)
    processor = Assembler(importer.output, queue.Queue(0), Processor)
    importer.threads = 1
    processor.threads = 1
    importer.start()
    processor.start()
    importer.input.put(entries)
    while (True):
        if (not processor.output.empty()) and (not paused):
            importer.input.put(processor.output.get())
        time.sleep(5)
        
main()
