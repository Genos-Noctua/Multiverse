# Multiverse version 8
import hashlib, time, os.path, shutil, tarfile, os
from pystray import Icon, Menu as menu, MenuItem as item
from tkinter.filedialog import *
from PIL import Image
import tkinter as tk

Service = temp = active = icon = files = None

def compress(pack):
    Service = pack['service']
    temp = pack['temp']
    _, head = os.path.split(pack['file'])
    archive = tarfile.open(Service + head + '.txz', 'w:xz')
    shutil.copyfile(pack['file'], temp + str(pack['depth']) + '-' + head)
    lol = [f for f in os.listdir(temp) if os.path.isfile(os.path.join(temp, f))]
    for name in lol:
        archive.add(temp + name, name)
    archive.close()
    shutil.rmtree(temp, True)

def decompress(pack):
    Service = pack['service']
    temp = pack['temp']
    _, head = os.path.split(pack['file'])
    archive = tarfile.open(Service + head + '.txz', 'r:*')
    archive.extractall(temp)
    archive.close()

def save(pack):
    Service = pack['service']
    temp = pack['temp']
    _, head = os.path.split(pack['file'])
    if os.path.isfile(Service + head + '.txz'):
        if os.path.isdir(temp): shutil.rmtree(temp, True)
        decompress(pack)
    else:
        os.makedirs(temp, exist_ok=True)
        pack['depth'] = 0
    compress(pack)
    pack['depth'] += 1

def hash(pack):
    with open(pack['file'], 'rb') as f:
        data = f.read()
        hash_object = hashlib.sha256(data)
        pack['sum'] = hash_object.hexdigest()
     
def Import(temps):
    global Service, temp
    if not os.path.isfile('files'):
        file = open('files', 'w+')
        file.close()
    with open('files', 'r') as file:
        string = file.read()
    if string == '':
        return list()
    files = str.split(string, sep='\n')
    newfiles = list()
    for x in temps:
        if x['file'] in files:
            newfiles.append(x)
            files.remove(x['file'])
    for x in files:
        pack = {}
        pack['file'] = x
        pack['depth'] = 0
        pack['service'] = Service
        pack['temp'] = temp
        _, head = os.path.split(pack['file'])
        if not os.path.isdir(Service):
            os.makedirs(Service)
        if os.path.isfile(Service + head + '.txz'):
            decompress(pack)
            temps = [f for f in os.listdir(temp) if os.path.isfile(temp + f)]
            pack['depth'] = len(temps)
            shutil.rmtree(temp, True)
        hash(pack)
        pack['prev'] = pack['sum']
        newfiles.append(pack)
    for pack in newfiles:
        hash(pack)
        if pack['prev'] != pack['sum']:
                pack['prev'] = pack['sum']
                save(pack)
    return newfiles

def on_clicked():
    window = tk.Tk()
    window.title('Edit File')

    text_box = tk.Text(window, height=20, width=100, font='Consolas 14')
    text_box.pack(expand=True, fill='both')

    with open('files', 'r') as file:
        text_box.insert('end', file.read())

    def save_changes():
        with open('files', 'w') as file:
            file.write(text_box.get('1.0', 'end-1c'))

    def open_files():
        files = askopenfilenames()
        for x in files[:-1]:
            text_box.insert('end', (x.replace('/', '\\') + '\n'))
        text_box.insert('end', files[-1])
        pass

    save_button = tk.Button(window, text='Save Changes', command=save_changes)
    save_button.pack()
    open_button = tk.Button(window, text='Open', command=open_files)
    open_button.pack()
    window.mainloop()

def onn():
    global active, icon, Service, temp
    active = 'active'
    with open('status', 'w+') as f:
        print('active', Service, temp, file=f, end='', sep='\n')
    with Image.open('Running.ico') as f:
        icon.icon = f

def off():
    global active, icon, Service, temp
    active = 'inactive'
    with open('status', 'w+') as f:
        print('inactive', Service, temp, file=f, end='', sep='\n')
    with Image.open('Sleeping.ico') as f:
        icon.icon = f

if __name__ == '__main__':
    if not os.path.isfile('status'):
        with open('status', 'w+') as _:
            print('inactive\nC:\\Multiverse service\\\nC:\\Multiverse service\\temp', file=_, end='')
        
    with open('status', 'r') as _:
        active, Service, temp = _.read().split(sep='\n')

    with Image.open('Running.ico') as f:
        icon = Icon('Multiverse', f, menu=menu(
            item('', on_clicked, visible=False, default=True),
            item('On', onn),
            item('Off', off)))
        icon.run_detached()

    if active == 'inactive': off()
    if active == 'active': onn()
    
    files = list()
    while True:
        if active == 'inactive': off()
        if active == 'active':
            onn()
            files = Import(files)
        time.sleep(120)