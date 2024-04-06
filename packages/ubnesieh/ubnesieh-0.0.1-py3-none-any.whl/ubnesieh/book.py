from ubnesieh.tools import cut_sentence, clean_book
from collections.abc import Iterable
from pathlib import Path
import glob


class Book(object):
    def __init__(self, path, symbol=True):
        self.path = Path(path)
        self._symbol = symbol

        self._text = None
        self._sentence = None
        self._half_sentence = None

    def open(self):
        path = self.path
        if path.is_dir():
            search = (path / '*').__str__()
            path = glob.glob(search)
            text = [open(i, mode='r', encoding='utf-8').read() for i in path]
            text = '\n'.join(text)
        else:
            text = open(path, mode='r', encoding='utf-8').read()
        return text

    @property
    def text(self):
        if self._text is None:
            self._text = self.open()
        return self._text

    @property
    def sentence(self):
        if self._sentence is None:
            text = clean_book(self.text)
            self._sentence = cut_sentence(text, cut_half=False, symbol=self._symbol)
        return self._sentence

    @property
    def half_sentence(self):
        if self._half_sentence is None:
            text = clean_book(self.text)
            self._half_sentence = cut_sentence(text, cut_half=True, symbol=self._symbol)
        return self._half_sentence
