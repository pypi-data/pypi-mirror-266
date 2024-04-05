import os
import json
from colorama import Fore, Style

class Database:
    def __init__(self, options={}):
        if not options.get('path') or not isinstance(options.get('path'), str):
            print(f"{Fore.RED} (Error) <MAIN> {Style.RESET_ALL}Invalid path!")
            return

        self.options = options
        self.options['logs'] = options.get('logs', True)

        split = options['path'].split('/')
        file = split.pop()
        dir = '/'.join(split) + '/'

        self.options['dir'] = dir
        self.options['file'] = file

        if not os.path.exists(dir):
            os.makedirs(dir)

        if not os.path.exists(dir + file):
            self.write({}, self.options)
        self.data = self.read(self.options)

    def read(self, options):
        try:
            with open(f"{options['dir']}{options['file']}", 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"{Fore.RED} (Error) <MAIN> {Style.RESET_ALL}Invalid parse!")
            exit(1)

    def write(self, data, options):
        try:
            with open(f"{options['dir']}{options['file']}", 'w') as file:
                json.dump(data, file, indent=2)
        except Exception as e:
            print(f"{Fore.RED} (ERROR) <MAIN> {Style.RESET_ALL}Invalid parse!")
            exit(1)

    def set(self, name, value):
        name = str(name)
        if str(value) == '' or name == '' or value is None:
            if self.options['logs']:
                print(f"{Fore.RED} (Warning) !!!SET!!! {Style.RESET_ALL}Invalid params!")
            return
        self.data[name] = value
        self.write(self.data, self.options)

    def get(self, name):
        name = str(name)
        if name == '':
            if self.options['logs']:
                print(f"{Fore.RED} (Warning) !GET! {Style.RESET_ALL}Invalid params!")
            return
        return self.data.get(name)

    def all(self):
        return self.read(self.options)

    def add(self, name, value):
        name = str(name)
        value = float(value)
        if str(value) == 'nan' or name == '':
            if self.options['logs']:
                print(f"{Fore.RED} (Warning) !!!ADD!!! {Style.RESET_ALL}Invalid params!")
            return
        self.data[name] = self.data.get(name, 0) + value
        self.write(self.data, self.options)

    def remove(self, name, value):
        name = str(name)
        value = float(value)
        if str(value) == 'nan' or name == '':
            if self.options['logs']:
                print(f"{Fore.RED} (Waning) !!REMOVE!! {Style.RESET_ALL}Invalid params!")
            return
        self.data[name] = self.data.get(name, 0) - value
        self.write(self.data, self.options)

    def push(self, name, value):
        name = str(name)
        if name == '' or value is None:
            if self.options['logs']:
                print(f"{Fore.RED} (warning) !PUSH! {Style.RESET_ALL}Invalid params!")
            return

        if not isinstance(self.data.get(name), list):
            if self.options['logs']:
                print(f"{Fore.RED} (Warning) !PUSH! {Style.RESET_ALL}''{name}'' is not Array type!")
            return

        result = self.data.get(name, [])
        result.append(value)
        self.data[name] = result
        self.write(self.data, self.options)

    def unpush(self, name, value):
        name = str(name)
        if name == '' or value is None:
            if self.options['logs']:
                print(f"{Fore.RED} (Warning) !PUSH! {Style.RESET_ALL}Invalid params!")
            return

        if not isinstance(self.data.get(name), list):
            if self.options['logs']:
                print(f"{Fore.RED} (Warning) !PUSH! {Style.RESET_ALL}''{name}'' is not Array type!")
            return

        result = self.data.get(name, [])
        if value in result:
            result.remove(value)
        else:
            if self.options['logs']:
                print(f"{Fore.RED} (Warning) !PUSH! {Style.RESET_ALL}''{value}'' not found in ''{name}''!")
        self.data[name] = result
        self.write(self.data, self.options)
