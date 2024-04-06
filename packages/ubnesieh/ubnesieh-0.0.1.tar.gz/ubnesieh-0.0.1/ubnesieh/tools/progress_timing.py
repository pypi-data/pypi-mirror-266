from time import time
from typing import Callable, Any
from abc import ABC, abstractmethod

from tqdm import tqdm

from .info import ClassInfo


class EpochProgressTiming(ClassInfo, ABC):

    def __init__(self, epoch, interval=120, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epoch = epoch
        self.progressbar = tqdm(range(epoch), desc=self.class_name)
        self._start_time = time()
        self._interval = interval

    def timing(self):
        flag = time() - self._start_time > self._interval
        if flag:
            self._start_time = time()
            self.timing_task()
        return flag

    def timing_task(self):
        return

    @abstractmethod
    def running(self):
        return

    def run(self):
        epoch = self.epoch
        running = self.running
        timing = self.timing
        progressbar = self.progressbar
        for ep in progressbar:
            kwargs = running()
            _timing = timing()
            progressbar.set_description('Epoch %s/%s' % (ep + 1, epoch))
            kwargs = kwargs if kwargs else {}
            kwargs['timing'] = _timing
            progressbar.set_postfix(**kwargs)

    __call__: Callable[..., Any] = run
