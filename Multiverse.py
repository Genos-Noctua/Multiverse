# Multiverse version 8
import hashlib, time, os.path, shutil, tarfile, os
from pystray import Icon, Menu as menu, MenuItem as item
from tkinter.filedialog import *
from Factory.factory import *
from PIL import Image
import tkinter as tk

Service, temp, active, icon, files = None, None, None, None, None

def compress(pack):
    Service = pack.payload['service']
    temp = pack.payload['temp']
    _, head = os.path.split(pack.payload['file'])
    archive = tarfile.open(Service + head + '.txz', 'w:xz')
    shutil.copyfile(pack.payload['file'], temp + str(pack.payload['depth']) + '-' + head)
    lol = [f for f in os.listdir(temp) if os.path.isfile(os.path.join(temp, f))]
    for name in lol:
        archive.add(temp + name, name)
    archive.close()
    shutil.rmtree(Service + 'temp', True)

def decompress(pack):
    Service = pack.payload['service']
    temp = pack.payload['temp']
    _, head = os.path.split(pack.payload['file'])
    archive = tarfile.open(Service + head + '.txz', 'r:*')
    archive.extractall(temp)
    archive.close()

def save(pack):
    Service = pack.payload['service']
    temp = pack.payload['temp']
    _, head = os.path.split(pack.payload['file'])
    if os.path.isfile(Service + head + '.txz'):
        if os.path.isdir(temp): shutil.rmtree(Service + 'temp', True)
        decompress(pack)
    else:
        os.makedirs(temp, exist_ok=True)
        pack.payload['depth'] = 0
    compress(pack)
    pack.payload['depth'] += 1

def where(pack):
    global Service, temp
    _, head = os.path.split(pack.payload['file'])
    if not os.path.isdir(Service):
        os.makedirs(Service)
    if os.path.isfile(Service + head + '.txz'):
        decompress(pack)
        temps = [f for f in os.listdir(temp) if os.path.isfile(temp + f)]
        pack.payload['depth'] = len(temps)
        shutil.rmtree(Service + 'temp', True)

def hash(pack):
    with open(pack.payload['file'], 'rb') as f:
        data = f.read()
        hash_object = hashlib.sha256(data)
        pack.payload['sum'] = hash_object.hexdigest()
     
def Import(temps, factory):
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
        if x.payload['file'] in files:
            newfiles.append(x)
            files.remove(x.payload['file'])
    for x in files:
        pack = factory.get_pack()
        pack.payload['file'] = x
        pack.payload['depth'] = 0
        pack.payload['service'] = Service
        pack.payload['temp'] = temp
        where(pack)
        hash(pack)
        pack.payload['prev'] = pack.payload['sum']
        newfiles.append(pack)
    return newfiles

def Process(pack):
    hash(pack)
    if pack.payload['prev'] != pack.payload['sum']:
            pack.payload['prev'] = pack.payload['sum']
            save(pack)
    pack.dst = 'out'
    return pack

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
    factory = Factory((Process, ), processes=1)

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

    files = list()
    while True:
        if active == 'inactive': off()
        if active == 'active':
            onn()
            files = factory.map(Import(files, factory))
            for x in files: x.dst = 0
        time.sleep(120)