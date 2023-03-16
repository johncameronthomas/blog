import json
import threading

class database:
    def __init__(self, path):
        self.path = path
        self.stack = []
        self.results = []
        try:
            open(self.path, 'x').close()
            f = open(self.path, 'w')
            f.write('{}')
            f.close()
        except:
            pass

    def start(self):
        self.stop_loop = False
        threading.Thread(target=self.loop).start()

    def stop(self):
        self.stop_loop = True

    def loop(self):
        while not self.stop_loop:
            for index, (id, action, arg) in enumerate(self.stack):
                f = open(self.path, 'r+')
                try:
                    data = json.load(f)
                except:
                    data = {}
                f.close()
                match action:
                    case 0: # dump
                        self.results.append((id, data))
                    case 1: # read
                        self.results.append((id, data[arg]))
                    case 2: # update
                        data[arg[0]] = arg[1]
                        f = open(self.path, 'w')
                        json.dump(data, f)
                        f.close()
                        self.results.append((id, None))
                    case 3: # remove
                        data.pop(arg)
                        f = open(self.path, 'w')
                        json.dump(data, f)
                        f.close()
                        self.results.append((id, None))
                self.stack.pop(index)

    def perform_action(self, action, arg):
        if len(self.stack) > 0:
            id = self.stack[-1][0] + 1
        else:
            id = 0
        self.stack.append((id, action, arg))
        while True:
            for index, (result_id, result) in enumerate(self.results):
                if result_id == id:
                    self.results.pop(index)
                    return result
                
    def dump(self):
        return self.perform_action(0, None)
    
    def read(self, key):
        return self.perform_action(1, key)
    
    def update(self, key, value):
        return self.perform_action(2, (key, value))
    
    def remove(self, key):
        return self.perform_action(3, key)