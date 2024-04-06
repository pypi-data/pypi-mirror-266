from typing import Callable, Any
from abc import ABC, abstractmethod
from torch import nn, Tensor
from torch.nn import Module
from torch.optim import Optimizer
from .tools import EpochProgressTiming, TorchIO


class DataGenerator(ABC):

    @abstractmethod
    def batch(self):
        return

    # __call__: Callable[..., Any] = batch


class TorchModelIO(TorchIO):
    def __init__(self, model: Module, ignore_load_error=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.ignore_load_error = ignore_load_error

    @property
    def data(self):
        return self.model.state_dict()

    def load(self):
        self.model.load_state_dict(self.loading(self.file_name)())

    def safe_load(self):
        f = self.load
        if self.ignore_load_error:
            try:
                f()
            except Exception as E:
                print(E)
        else:
            f()


class TrainBase(EpochProgressTiming, TorchModelIO, ABC):
    def __init__(
            self,
            model: Module,
            optimizer: Optimizer,
            epoch,
            interval,
            cuda,
            clip_grad=20,
    ):
        super().__init__(epoch=epoch, interval=interval, model=model)

        self.model = model
        self.optimizer = optimizer
        self.clip_grad = clip_grad

        self.safe_load()
        if cuda:
            self.model.cuda()

    @abstractmethod
    def forward(self) -> Tensor:
        ...

    def timing_task(self):
        self.save()

    def running(self):
        self.optimizer.zero_grad()
        loss = self.forward()
        loss.backward()
        if self.clip_grad is not None:
            nn.utils.clip_grad_norm_(
                self.model.parameters(),
                max_norm=self.clip_grad,
                norm_type=2)
        self.optimizer.step()
        loss = float(loss.detach().cpu().data)
        msg = {'loss': loss}
        return msg
