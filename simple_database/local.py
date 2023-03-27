import threading
import json

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
            try:
                for index, (id, action, arg) in enumerate(self.stack):
                    f = open(self.path, 'r')
                    data = json.load(f)
                    f.close()
                    match action:
                        case 0: # dump
                            self.results.append((id, data))
                        case 1: # read
                            keys = arg
                            for key in keys:
                                data = data[key]
                            self.results.append((id, data))
                        case 2: # write
                            value = arg[0]
                            keys = arg[1]
                            exec_str = 'data'
                            for key in keys:
                                exec_str += "['{}']".format(key)
                            exec_str += '=value'
                            exec(exec_str)
                            f = open(self.path, 'w')
                            json.dump(data, f)
                            f.close()
                            self.results.append((id, None))
                        case 3: # remove
                            keys = arg
                            exec_str = 'data'
                            for key in keys[0:-1]:
                                exec_str += "['{}']".format(key)
                            exec_str += '.pop(keys[-1])'
                            exec(exec_str)
                            f = open(self.path, 'w')
                            json.dump(data, f)
                            f.close()
                            self.results.append((id, None))
                    self.stack.pop(index)
            except:
                pass

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

    def read(self, *keys):
        return self.perform_action(1, keys)

    def write(self, value, *keys):
        return self.perform_action(2, (value, keys))

    def remove(self, *keys):
        return self.perform_action(3, keys)