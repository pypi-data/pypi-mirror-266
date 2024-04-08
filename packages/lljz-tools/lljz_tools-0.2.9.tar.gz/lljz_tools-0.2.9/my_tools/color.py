"""
@file   : color.py
@author : jiangmenggui@hosonsoft.com
@data   : 2024/4/2
"""


class _Color:

    def __init__(self, s, start, end, name):
        self.raw = s
        self.s = start + s + end
        self.start = start
        self.end = end
        self.name = name

    def __len__(self):
        return self.raw.__len__()

    def __str__(self):
        return self.s.__str__()

    def __repr__(self):
        return self.s.__repr__()

    def __iter__(self):
        return self.raw.__iter__()

    def __add__(self, other):
        return self.s + other

    def __format__(self, format_spec):
        return self.start + self.raw.__format__(format_spec) + self.end


class _ColorFactory:

    def __init__(self, name, start, end='\033[0m'):
        self.name = name
        self.start = start
        self.end = end

    def __call__(self, s: str):
        return _Color(s, self.start, self.end, self.name)


class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    red = _ColorFactory('red', FAIL)
    green = _ColorFactory('green', OKGREEN)
    yellow = _ColorFactory('yellow', WARNING)
    blue = _ColorFactory('blue', OKBLUE)
    cyan = _ColorFactory('cyan', OKCYAN)


if __name__ == '__main__':

    pass
