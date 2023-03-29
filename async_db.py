import threading
import json
from queue import Queue

class Database:
    def __init__(self, path):
        self.path = path
        self.task_performer = threading.Thread(target=self.perform_tasks)
        self.tasks = Queue(maxsize=20)
        try:
            open(self.path, 'x').close()
            f = open(self.path, 'w')
            f.write('{}')
            f.close()
        except:
            pass

    def read_file(self):
        f = open(self.path, 'r')
        data = json.load(f)
        f.close()
        return data

    def write_file(self, data):
        f = open(self.path, 'w')
        json.dump(data, f)
        f.close()

    def perform_tasks(self):
        while True:
            task = self.tasks.get()
            command, arg, result = task
            data = self.read_file()
            match command:
                case 0: # dump
                    result.put(data)
                case 1: # read
                    for key in arg:
                        data = data[key]
                    result.put(data)
                case 2: # initialize
                    self.write_file(arg)
                    result.put(None)
                case 3: # write
                    value, keys = arg[0], arg[1]
                    exec_str = 'data'
                    for key in keys:
                        exec_str += "['{}']".format(key)
                    exec_str += '=value'
                    exec(exec_str)
                    self.write_file(data)
                    result.put(None)
                case 4: # clear
                    self.write_file({})
                    result.put(None)
                case 5: # remove
                    exec_str = 'data'
                    for key in arg[0:-1]:
                        exec_str += "['{}']".format(key)
                    exec_str += '.pop(arg[-1])'
                    exec(exec_str)
                    self.write_file(data)
                    result.put(None)
                case 6: # quit
                    result.put(None)
                    return

    def perform_task(self, command, arg):
        if self.task_performer.is_alive():
            task = (command, arg, Queue(maxsize=1))
            self.tasks.put(task)
            return task[2].get()
        else:
            raise ValueError()

    def start(self):
        if not self.task_performer.is_alive():
            self.task_performer = threading.Thread(target=self.perform_tasks)
            self.task_performer.start()
        else:
            raise ValueError()

    def stop(self):
        if self.task_performer.is_alive():
            self.perform_task(6, None)
            self.task_performer.join()
        else:
            raise ValueError()

    def dump(self):
        return self.perform_task(0, None)

    def read(self, *keys):
        return self.perform_task(1, keys)

    def initialize(self, value):
        return self.perform_task(2, value)

    def write(self, value, *keys):
        return self.perform_task(3, (value, keys))

    def clear(self):
        return self.perform_task(4, None)

    def remove(self, *keys):
        return self.perform_task(5, keys)