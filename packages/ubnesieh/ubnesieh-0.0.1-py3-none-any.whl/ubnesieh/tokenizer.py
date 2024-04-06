from .tools import by_pinyin, PickleIO
from collections.abc import Iterable


def append_default_placeholders(origin_list, default_placeholders):
    if default_placeholders:
        default_placeholders.reverse()
        for i in default_placeholders:
            origin_list.remove(i) if i in origin_list else None
            origin_list.insert(0, i)
    return origin_list


def tokenize(elements, default_placeholders: list = None):
    assert isinstance(elements, Iterable)
    char_set = set(elements)
    char_list = list(char_set)
    char_list.sort(key=by_pinyin)
    char_list = append_default_placeholders(char_list, default_placeholders)
    index = [i for i in range(len(char_list))]
    index_char = dict(zip(index, char_list))
    char_index = dict(zip(char_list, index))
    return index_char, char_index


class Tokenizer(PickleIO):
    def __init__(self, elements, placeholders=None):
        self.i2c, self.c2i = tokenize(elements, placeholders)
        self.size = len(self.i2c)

    def __call__(self, query, recursive=True):
        if isinstance(query, Iterable) and (not isinstance(query, str)):
            return [self.__call__(i) for i in query]
        index = self.c2i
        return index[query]

    def reverse(self, query):
        if isinstance(query, Iterable):
            return [self.reverse(i) for i in query]
        index = self.i2c
        return index[query]

    def r(self, query):
        return self.reverse(query)
