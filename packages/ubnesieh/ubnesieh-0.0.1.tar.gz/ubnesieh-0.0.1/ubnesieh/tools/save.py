from types import FunctionType
from abc import ABC, abstractmethod
from pathlib import Path
from .info import CommonInfo
import pickle
import torch


class BaseIO(ABC):
    @property
    @abstractmethod
    def file_name(self):
        return

    @property
    @abstractmethod
    def data(self):
        return

    @staticmethod
    @abstractmethod
    def saving(obj, file_name) -> FunctionType:
        ...

    @staticmethod
    @abstractmethod
    def loading(file_name) -> FunctionType:
        ...

    def save(self):
        self.saving(self.data, self.file_name)()

    def load(self):
        obj = self.loading(self.file_name)()
        return obj


class PickleIO(CommonInfo, BaseIO):
    @property
    def file_name(self):
        path = self.mk_subdir_for_current_directory(subdir='cache')
        template = '{name1}-{name2}.{extention}'
        name = template.format(
            name1=self.current_file_name,
            name2=self.class_name.lower(),
            extention='pickle')
        name = path / name
        return name

    def saving(self, obj, file_name):
        f = lambda: pickle.dump(obj=obj, file=open(file_name, mode='wb'))
        return f

    def loading(self, file_name) -> FunctionType:
        f = lambda: pickle.load(file=open(file_name, mode='rb'))
        return f


class TorchIO(CommonInfo, BaseIO):
    @property
    def file_name(self):
        path = self.mk_subdir_for_current_directory(subdir='cache')
        template = '{name1}-{name2}.{extention}'
        name = template.format(
            name1=self.current_file_name,
            name2=self.class_name.lower(),
            extention='pth')
        name = path / name
        return name

    def saving(self, obj, file_name):
        f = lambda: torch.save(obj=obj, f=file_name)
        return f

    def loading(self, file_name) -> FunctionType:
        f = lambda: torch.load(f=file_name)
        return f
