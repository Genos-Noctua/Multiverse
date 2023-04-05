import threading, time
class Assembler:
    threads = 2
    
    def run(self):
        while True:
            if self.input.unfinished_tasks == 0:
                time.sleep(0.2)
                continue
            self.task(self)

    def __init__(self, input, output, task):
        self.input = input
        self.output = output
        self.task = task

    def start(self):
        self.ths = list(range(self.threads))
        for t in range(self.threads):
            self.ths[t] = threading.Thread(target=self.run, args = ())
            self.ths[t].daemon = True
            self.ths[t].start()

    def kill(self):
        for t in range(self.threads):
            self.ths[t].terminate()
        del(self.ths)
        del(self.input)
        del(self.output)
        del(self.task)

        
'''
import queue
from Assembler import *

class Batch:
    def __init__(self, x, y):
        pass

def Task(node):
    x = node.input.get()
    node.output.put(x*2)
            
node = Assembler(queue.Queue(0), queue.Queue(0), Task)
node.start()
for x in range(10):
    node.input.put(x)

for x in range(10):
    print(node.output.get())

node.kill
'''