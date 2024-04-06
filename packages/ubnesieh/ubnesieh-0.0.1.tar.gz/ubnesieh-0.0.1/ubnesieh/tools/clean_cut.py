import re


def get_chinese_char(text, separator=''):
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    match = zh_pattern.findall(text)
    _match = separator.join(match)
    return _match


def has_chinese_char(text):
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    match = zh_pattern.search(text)
    return True if match else False


def is_topic(text: str):
    return text.startswith('#')


def text_filter(text: str):
    condition = (not text.isdigit()) and (text.isalpha() or has_chinese_char(text))
    return condition


def cut_sentence(text, min_length=2, drop_topic=True, cut_half=True, symbol=True):
    if cut_half:
        p = r'([\，\,\：\！\？\｡\。\～\…\r\n\”\’\—\.\》])' \
            if symbol else r'[\，\,\：\！\？\｡\。\～\…\r\n\“\”\‘\’\—\.\《\》]'
        _text = re.split(p, text)
    else:
        p = r'([\！\？\｡\。\～\…\r\n])' if symbol else r'[\！\？\｡\。\～\…\r\n]'
        _text = re.split(p, text)
    _text = [i.strip() for i in _text]
    if symbol:
        _text.append("")
        _text = ["".join(i) for i in zip(_text[0::2], _text[1::2])]
    _text = [i for i in _text if (len(i) >= min_length and i and text_filter(i))]
    if drop_topic:
        _text = [i for i in _text if not is_topic(i)]
    return _text


def clean_book(book):
    # book = re.sub(r'-+', '-', book)
    book = re.sub(r'-+', '\n', book)
    book = re.sub(r' +', ' ', book)
    book = re.sub(r'　+', '　', book)

    # book = re.sub(r'-+', '--', book)
    # book = re.sub(r' +', '  ', book)
    # book = re.sub(r'　+', '　　', book)

    book = re.sub(r'\n+', '\n', book)
    return book
