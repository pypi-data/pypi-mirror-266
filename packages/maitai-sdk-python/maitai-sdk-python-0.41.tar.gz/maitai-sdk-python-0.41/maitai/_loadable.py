import re

pattern = re.compile(r'(?<!^)(?=[A-Z])')


class Loadable:

    def __init__(self):
        pass

    def load(self, **args):
        args_snake = {}
        for k, v in args.items():
            if isinstance(v, list) and len(v) > 0:
                v = self.load_list(v)
            elif isinstance(v, dict):
                v = self.load_subobject(**v)
                print(f'Setting {k} to {v}')
            args_snake[self.snake(k)] = v
        self.__dict__.update(args_snake)
        return self

    def load_subobject(self, **args):
        args_snake = {}
        for k,v in args.items():
            if isinstance(v, dict):
                v = self.load_subobject(**v)
            args_snake[self.snake(k)] = v
        return args_snake

    def load_list(self, list_obj):
        tmp = []
        for v in list_obj:
            if isinstance(v, list) and len(v) > 0:
                v = self.load_list(v)
            elif isinstance(v, dict):
                v = self.load_subobject(**v)
            tmp.append(v)
        return tmp

    def snake(self, orig):
        return pattern.sub('_', orig).lower()