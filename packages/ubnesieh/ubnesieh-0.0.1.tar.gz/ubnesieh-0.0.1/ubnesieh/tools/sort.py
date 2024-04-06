from hashlib import md5
from itertools import chain
from pypinyin import pinyin, Style


def by_pinyin(s: str):
    m = md5()
    m.update(s.encode())
    h = m.hexdigest()[-8:]
    y = ''.join(chain.from_iterable(pinyin(s, style=Style.TONE3))) + h
    y = str(len(s)) + y
    return y
