import sys


class ClassInfo(object):
    @property
    def class_name(self):
        name = type(self).__name__
        return name

    @property
    def class_file(self):
        file = sys.modules[self.__class__.__module__].__file__
        return file
