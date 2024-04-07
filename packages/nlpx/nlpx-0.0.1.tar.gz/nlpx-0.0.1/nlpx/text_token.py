import re
import operator
from pathlib import Path
from functools import reduce
from typing import List, Union, Iterable, Any

UTF8 = 'utf-8'
REMOVE_CHARS = '[·’!"\#$%&\'()＃！（）*+,-./:;<=>?\@，：?￥★、…．＞【】［］《》？“”‘’\[\\]^_`{|}~]+'


# -----------------------------------------------------------Read file-------------------------------------------------------------------
def read_file(path: str, encoding=UTF8):
    """
    读取文件内容
    :param path: 文件名，不能是文件夹
    :param encoding: 编码
    :return: 包含非空文本行的生成器，如 ['上课时学生手机响个不停，老师一怒之下把手机摔了。', '家长拿发票让老师赔', ...]
    """
    # if Path(path).stat().st_size <= 10000: #1048576000: # 小于等于1G
    with open(path, encoding=encoding) as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]


def read_large_file(path: str, encoding=UTF8):
    with open(path, encoding=encoding) as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


async def async_read_file(path: str, encoding=UTF8):
    return read_file(path, encoding)


def read_corpus_files(path: str, encoding=UTF8, pattern='*', func=read_file, async_func=async_read_file):
    """
    读取文件或文件夹下所有符合条件的文件
    :param path: 文件或文件夹， 如：'./train.txt'. 如果是文件夹，会读取文件夹下的所有目录和文件.
    :param encoding: 编码
    :param suffix: 文件后缀，当path是文件夹的时候，会根据此后缀过滤文件
    :param func: 具体读取文件的读函数，默认是read_file，可替换。注意：其函数签名为 function_name(path: str, encoding: str) -> corpus: Iterable[str]
    :param async_func: 传入文件夹时的读函数，用协程读取每个文件，默认是async_read_file，可替换。注意：其函数签名为 async function_name(path: str, encoding: str) -> corpus: Iterable[str]
    :return: 非空文本行，如 ['上课时学生手机响个不停，老师一怒之下把手机摔了。', '家长拿发票让老师赔', ...]
    """
    path = Path(path)
    if path.is_file():
        return func(path, encoding)

    import asyncio
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(async_func(file, encoding)) for file in path.rglob(pattern)]  # 这里不能用map，否则读不出数据
    wait_coro = asyncio.wait(tasks)
    loop.run_until_complete(wait_coro)
    all_lines = (task.result() for task in tasks)
    loop.close()

    return reduce(operator.iconcat, all_lines, [])


def load_embedding(path: str, is_large_file=False):
    if path.endswith('.bz2'):
        return load_embedding_from_bz2(path, is_large_file)
    return load_embedding_nomal(path, is_large_file)


def load_embedding_from_bz2(path: str, is_large_file=False):
    import bz2
    if is_large_file:
        with bz2.open(path, 'r') as f:
            tokens, vecs = _get_token_vecs(f, require_decode_token=True)
        return list(tokens), list(vecs)

    with bz2.open(path, 'r') as f:
        lines = f.readlines()
    return _handle_lines(lines, require_decode_token=True)


def load_embedding_nomal(path: str, is_large_file=False):
    if is_large_file:
        with open(path, 'r', encoding=UTF8) as f:
            tokens, vecs = _get_token_vecs(f, require_decode_token=False)
        return list(tokens), list(vecs)

    with open(path, 'r', encoding=UTF8) as f:
        lines = f.readlines()
    return _handle_lines(lines, require_decode_token=False)


def _get_token_vecs(f, require_decode_token):
    token_vec = (_handle_line(line, require_decode_token) for line in f if len(line.rstrip().split()) > 2)
    return zip(*token_vec)


def _handle_lines(lines: Iterable[str], require_decode_token: bool):
    if len(lines[0].split()) <= 2:
        lines = lines[1:]
    token_vec = list(map(lambda line: _handle_line(line, require_decode_token), lines))
    tokens, vecs = zip(*token_vec)
    return list(tokens), list(vecs)


def _handle_line(line: str, require_decode_token: bool):
    def get_vec(elems):
        return list(map(float, elems))

    elems = line.rstrip().split()
    return elems[0].decode(UTF8) if require_decode_token else elems[0], get_vec(elems[1:])


# ----------------------------------------------------------Token cut--------------------------------------------------------------------
def cut_char(sentence: str):
    """
    把句子按字分开，不破坏英文结构
    """
    # 首先分割 英文 以及英文和标点
    pattern_char_1 = re.compile(r'([\W])')
    parts = pattern_char_1.split(sentence)
    parts = [p for p in parts if len(p.strip()) > 0]
    # 分割中文
    pattern = re.compile(r'([\u4e00-\u9fa5])')
    chars = pattern.split(sentence)
    return [w for w in chars if len(w.strip()) > 0]


def batch_cut(text: Iterable[str], language='cn', cut_type='word', keep_punctuation=False):
    """
    多句话批量分词
    :param text: 多句话，即多行
    :param language: 哪国语言，支持cn和en
    :param cut_type: 按词还是字分，支持word和char
    :param keep_punctuation: 是否保留标点符号
    :return: 分词后的list(2维)
    """
    import re
    if language == 'cn':
        import jieba
        replace_char = ''
        if cut_type == 'word':
            if keep_punctuation:
                def fn(s):
                    return jieba.cut(s.strip())
            else:
                def fn(s):
                    return jieba.cut(re.sub(REMOVE_CHARS, replace_char, s.strip()))
        else:
            if keep_punctuation:
                def fn(s):
                    return cut_char(s.strip())
            else:
                def fn(s):
                    return cut_char(re.sub(REMOVE_CHARS, replace_char, s.strip()))
        return map(fn, text)
        # return [cut_char(re.sub(REMOVE_CHARS, '', line.strip())) for line in text]

    if language == 'en':
        replace_char = ' '
        if cut_type == 'word':
            def fn(s):
                return re.sub(REMOVE_CHARS, replace_char, s).strip().lower().split()
        else:
            if keep_punctuation:
                def fn(s):
                    return list(s.strip().lower())
            else:
                def fn(s):
                    return list(re.sub('[^A-Za-z]+', replace_char, s).strip().lower())
        return map(fn, text)
        # return [fn(line) for line in text]

    raise NotImplementedError(f'暂时未实现"{language}"的分词功能')


def cut(sentence: str, language='cn', cut_type='word', keep_punctuation=False):
    """
    单句话分词
    :param sentence: 单句话，即一行
    :param language: 哪国语言，支持cn和en
    :param cut_type: 按词还是字分，支持word和char
    :param keep_punctuation: 是否保留标点符号
    :return: 分词后的list(1维)
    """
    import re
    if language == 'cn':
        import jieba
        replace_char = ''
        if cut_type == 'word':
            if keep_punctuation:
                return list(jieba.cut(sentence.strip()))
            else:
                return list(jieba.cut(re.sub(REMOVE_CHARS, replace_char, sentence.strip())))
        else:
            if keep_punctuation:
                return cut_char(sentence.strip())
            else:
                return cut_char(re.sub(REMOVE_CHARS, replace_char, sentence.strip()))

    if language == 'en':
        replace_char = ' '
        if cut_type == 'word':
            return re.sub(REMOVE_CHARS, replace_char, sentence).strip().lower().split()
        else:
            if keep_punctuation:
                return list(sentence.strip().lower())
            else:
                return list(re.sub('[^A-Za-z]+', replace_char, sentence).strip().lower())

    raise NotImplementedError(f'暂时未实现"{language}"的分词功能')


# ----------------------------------------------------------Token counter-------------------------------------------------------------------
def token_counter(cut_corpus: Union[map, Iterable[str], Iterable[Iterable[str]]]):
    """
    统计词频
    :param cut_corpus: 分词后的语料
    :return: collections.Counter, 可以用items()方法取出[tuple(word, count)]
    """
    from collections import Counter
    if isinstance(cut_corpus, map) or (isinstance(cut_corpus, Iterable) and isinstance(cut_corpus[0], Iterable)):
        # return Counter([token for line in batch_cut for token in line])
        return Counter(reduce(operator.iconcat, cut_corpus, []))
    elif isinstance(cut_corpus, Iterable) and isinstance(cut_corpus[0], str):
        return Counter(cut_corpus)
    raise TypeError("'cut_corpus'参数类型不对")


# ----------------------------------------------------------Text analysis-------------------------------------------------------------------
def show_label_category_count(labels):
    """
    :param corpus: 语料，可以是Iterable[str], Iterable[Iterable[str]], pandas的Series[str]
    :return: labels, label_count
    """
    import sys
    import pandas as pd
    import matplotlib.pyplot as plt
    if isinstance(labels, pd.Series):
        label_count = labels.value_counts(sort=False)
        label_count.plot(kind='bar')
        labels = labels.unique()
        min_count, max_count = label_count.min(), label_count.max()
    else:
        from collections import Counter
        label_count = Counter(labels)

        labels, counts = [], []
        min_count, max_count = sys.maxsize, 0
        for label, count in label_count.items():
            labels.append(label)
            counts.append(count)
            min_count = count if min_count > count else min_count
            max_count = count if max_count < count else max_count

        plt.bar(labels, counts, width=0.5)
        plt.xticks(ticks=labels, rotation=60)

    print(f'最大值: {max_count}，最小值: {min_count}，相差{max_count / min_count:.0f}倍')
    plt.show()
    return labels, label_count


def show_sentence_len_hist(corpus, language='cn', cut_type='word', bins=50, scope: tuple = None):
    """
    :param corpus: 语料，可以是Iterable[str], Iterable[Iterable[str]], pandas的Series[str]
    :param language:
    :param cut_type:
    :param bins:
    :param scope:
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    if isinstance(corpus, pd.Series):
        sent_length = corpus.map(lambda x: len(cut(x, language, cut_type)))
        sent_length.hist(bins=bins)
    else:
        batch_cuts = batch_cut(corpus, language, cut_type)
        length = list(map(lambda s: len(s), batch_cuts))
        if scope:
            length = [x for x in length if scope[0] <= x <= scope[1]]
        print(f'最短的句子是{min(length)}，最长为{max(length)}')
        plt.hist(length, bins=bins)
    plt.xlabel('sentence length')
    plt.ylabel('sentence count')
    plt.grid()
    plt.show()


def show_token_frequency_plot(corpus, language='cn', cut_type='word', scope: tuple = None):
    """
    :param corpus: 语料，可以是Iterable[str], Iterable[Iterable[str]], pandas的Series[str]
    :param language:
    :param cut_type:
    :param scope:
    """
    import math
    import pandas as pd
    import matplotlib.pyplot as plt
    show_num = 10
    batch_cuts = batch_cut(corpus, language, cut_type)
    counter = token_counter(batch_cuts)
    sorted_token_count = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)
    print(f'出现频率最大的{show_num}个token:\n {sorted_token_count[:show_num]}')
    print(f'出现频率最小的{show_num}个token:\n {sorted_token_count[-show_num:]}')
    if scope is not None:
        sorted_token_count = sorted_token_count[scope[0]:scope[1]]

    sorted_count = list(map(lambda kv: kv[1], sorted_token_count))

    # sorted_count = sorted(counter.values(), reverse=True)
    # if scope is not None:
    #     token_count = sorted_count[scope[0]:scope[1]]

    plt.plot(list(map(lambda n: math.log(n), sorted_count)))
    # plt.plot(sorted_count, scalex='log', scaley='log')
    plt.xlabel('token:x')
    plt.ylabel('frequency:log(x)')
    plt.show()


# ----------------------------------------------------------pad function--------------------------------------------------------------------
def _pad(tokens: Iterable[int], max_length: int = None, truncation=True, padding=True, padding_side='right', pad_begin_end=False,
        pad_value=0, bos_value=1, eos_value=2):
    """
    pad token list(1维)
    :return: padded list, valid_size size
    """
    assert padding_side in ('right', 'left'), '参数padding_side只能是"right"或"left".'
    size = len(tokens)
    if pad_begin_end:
        size += 2
        if max_length and truncation and size > max_length:
            return [bos_value] + tokens[:max_length - 2] + [eos_value], max_length
        if max_length and padding and size < max_length:
            if padding_side == 'right':
                return [bos_value] + tokens + [eos_value] + [pad_value] * (max_length - size), size
            elif padding_side == 'left':
                return [pad_value] * (max_length - size) + [bos_value] + tokens + [eos_value], size
            raise ValueError(f'参数"padding_side"错误: {padding_side}')
        return [bos_value] + tokens + [eos_value], size
    else:
        if max_length and truncation and size > max_length:
            return tokens[:max_length], max_length
        if max_length and padding and size < max_length:
            if padding_side == 'right':
                return tokens + [pad_value] * (max_length - size), size
            elif padding_side == 'left':
                return [pad_value] * (max_length - size) + tokens, size
            raise ValueError(f'参数"padding_side"错误: {padding_side}')
        return tokens, size


def pad(tokens: Iterable[int], max_length: int = None, truncation=True, padding=True, padding_side='right', pad_begin_end=False,
        pad_value=0, bos_value=1, eos_value=2):
    """
    :param tokens: (1维)
    :param max_length:
    :param truncation:
    :param padding:
    :param padding_side:
    :param pad_begin_end:
    :param pad_value:
    :param bos_value:
    :param eos_value:
    :return: padded list
    """
    return _pad(tokens, max_length, truncation, padding, padding_side, pad_begin_end, pad_value, bos_value, eos_value)[0]


def batch_pad(batch: Union[map, Iterable[Iterable[int]]], max_length: int = None, truncation=True, padding=True, padding_side='right',
        pad_begin_end=False, pad_value=0, bos_value=1, eos_value=2):
    """
    :param batch: (2维)
    :return:
    """
    if not max_length:
        max_length = max(len(item) for item in batch)
    return list(map(lambda tokens: pad(tokens, max_length, truncation, padding, padding_side, pad_begin_end, pad_value, bos_value, eos_value), batch))


def _pad_mask(tokens: Iterable[int], max_length: int = None, truncation=True, padding=True, padding_side='right', pad_begin_end=False,
        pad_value=0, bos_value=1, eos_value=2):
    input_ids, real_size = _pad(tokens, max_length, truncation, padding, padding_side, pad_begin_end, pad_value, bos_value, eos_value)
    size = len(input_ids)
    if size > real_size:
        if padding_side == 'right':
            return input_ids, [1] * real_size + [0] * (size - real_size)
        return input_ids, [0] * (size - real_size) + [1] * real_size
    else:
        return input_ids, [1] * size


def pad_mask(tokens: Iterable[int], max_length: int = None, truncation=True, padding=True, padding_side='right', pad_begin_end=False,
        pad_value=0, bos_value=1, eos_value=2):
    input_ids, mask_ids = _pad_mask(tokens, max_length, truncation, padding, padding_side, pad_begin_end, pad_value, bos_value, eos_value)
    return {'input_ids': input_ids, 'mask_ids': mask_ids}


def batch_pad_mask(batch: Union[map, Iterable[Iterable[int]]], max_length: int = None, truncation=True, padding=True, padding_side='right',
        pad_begin_end=False, pad_value=0, bos_value=1, eos_value=2):
    if not max_length:
        max_length = max(len(item) for item in batch)
    ids = list(
        map(lambda tokens: _pad_mask(tokens, max_length, truncation, padding, padding_side, pad_begin_end, pad_value, bos_value, eos_value), batch))
    input_ids, mask_ids = zip(*ids)
    return {'input_ids': list(input_ids), 'mask_ids': list(mask_ids)}


# ---------------------------------------------------------Tokenizer class---------------------------------------------------------------------
class BaseTokenizer:
    """
    encode返回的是 list
    """
    SAVE_SEP = '|'
    PAD, UNK, BOS, EOS, SEP = '<pad>', '<unk>', '<bos>', '<eos>', '<sep>'
    BACKUP_TOKENS = [PAD, UNK, BOS, EOS, SEP]

    def __init__(self, file: str = None, corpus: Iterable[str] = None, cut_corpus: Iterable[Iterable[str]] = None, vocab: Iterable[str] = None,
            min_frequency=0, reserved_token=[], language='cn', cut_type='word', word_frequency=False):
        """
        :param file: 语料文件，可以是文件也可以是文件夹， 如：'./train.txt'. 如果是文件夹，会读取文件夹下的所有目录和文件.
        :param corpus: 语料，每个元素是一句话，如：['上课时学生手机响个不停，老师一怒之下把手机摔了。', '家长拿发票让老师赔', ...]
        :param cut_corpus: 语料，每个元素是是分词后的一句话，如：[['上课', '时', '学生', '手机', '响', '个', '不停'], ['家长', '拿', '发票', '让', '老师', '赔']]
        :param vocab: 词表，如：['上课', '学生', '手机', '不停', '，', '老师']
        :param min_frequency: 最小词频，小于词词频的词会被忽略，默认是0，所有的词都保留
        :param reserved_token: 保留token, 如 '<pad>', '<unk>'等
        :param language: 语言 'cn'和'en'
        :param cut_type: 分词类型，只支持'word'和‘char'两种类型
        :param word_frequency: 是否统计词频
        """
        self.language = language
        self.cut_type = cut_type
        self.reserved_token = self.BACKUP_TOKENS + [token for token in reserved_token if token not in self.BACKUP_TOKENS]
        if vocab is not None:
            for token in [token for token in self.reserved_token if token in vocab]:
                vocab.remove(token)
            self.vocab = self.reserved_token + vocab
            self.token_to_idx = {k: i for i, k in enumerate(self.vocab)}
        else:
            if file is not None and corpus is None:
                corpus = read_corpus_files(file)
            if corpus is not None:
                cut_corpus = batch_cut(corpus, language=language, cut_type=cut_type, keep_punctuation=True)
            if cut_corpus is not None:
                counter = token_counter(cut_corpus)
                sorted_token_frequency = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)
                self.vocab = self.reserved_token.copy()
                self.vocab += [token for token, freq in sorted_token_frequency if freq >= min_frequency and token not in self.vocab]
                self.token_to_idx = {k: i for i, k in enumerate(self.vocab)}
                if word_frequency:
                    self.word_frequency = [(self.token_to_idx[token], freq) for token, freq in sorted_token_frequency if
                                           token not in self.reserved_token]
            else:
                raise ValueError('参数file, corpus, vocab不能同时为None.')
        self.vocab_size = len(self.vocab)
        self.pad, self.unk, self.bos, self.eos, self.sep = [self.token_to_idx[token] for token in self.BACKUP_TOKENS]

    def encode(self, sentence: str, max_length: int = None, truncation=True, padding=True, padding_side='right',
            pad_begin_end=False, keep_punctuation=False, is_split_into_words: bool = False):
        """
        :param sentence: '上课时学生手机响个不停，老师一怒之下把手机摔了'
        :param max_length:
        :param truncation:
        :param padding:
        :param padding_side:
        :param pad_begin_end:
        :param keep_punctuation: 是否保留标点符号
        :param is_split_into_words: 是否已经分词
        :return:
        """
        if isinstance(sentence, str):
            if is_split_into_words:
                tokens = self.do_encode(sentence)
            else:
                tokens = cut(sentence, self.language, self.cut_type, keep_punctuation=keep_punctuation)
                tokens = self.do_encode(tokens)
            return self.padding(tokens, max_length, truncation, padding, padding_side, pad_begin_end)

        raise ValueError('参数"sentence"类型错误')

    def batch_encode(self, sentences: Union[Iterable[str], Iterable[Iterable]], max_length: int = None, truncation=True, padding=True, padding_side='right',
            pad_begin_end=False, keep_punctuation=False, is_split_into_words: bool = False):
        """
        :param sentences: ['上课时学生手机响个不停，老师一怒之下把手机摔了。', '家长拿发票让老师赔', ....]
        :param max_length:
        :param truncation:
        :param padding:
        :param padding_side:
        :param pad_begin_end:
        :param keep_punctuation: 是否保留标点符号
        :param is_split_into_words: 是否已经分词
        :return:
        """
        if isinstance(sentences, Iterable):
            if is_split_into_words:
                tokens = map(self.do_encode, sentences)
            else:
                batch_cuts = batch_cut(sentences, language=self.language, cut_type=self.cut_type, keep_punctuation=keep_punctuation)
                tokens = map(self.do_encode, batch_cuts)
            return self.padding(tokens, max_length, truncation, padding, padding_side, pad_begin_end)

        raise ValueError('参数"sentence"类型错误')

    def do_encode(self, cut_tokens: Union[str, Iterable[str]]):
        """
        把词转换成数字
        :param cut_tokens: '学生' 或 ['学生', '手机', '老师']
        :return:
        """
        if isinstance(cut_tokens, str):
            return self.token_to_idx.get(cut_tokens, self.unk)
        return list(map(self.do_encode, cut_tokens))

    def decode(self, tokens: Iterable[int], return_special_tokens=False, return_sentence=False):
        """
        :param tokens: [2, 19, 27, 3, 0, 0]
        :param return_special_tokens: 是否返回'<pad>', '<unk>', '<bos>', '<eos>'等特殊字符
        :param return_sentence: 返回的是一句话还是词序列
        :return: 由return_sentence决定，返回的是 '上课时学生手机响个不停‘, 还是 ['上课', '时', '学生', '手机', ’响个, '不停']
        """
        return [self.decode(index, return_special_tokens, return_sentence) for index in tokens]

    def batch_decode(self, tokens: Iterable[Iterable[int]], return_special_tokens=False, return_sentence=False):
        """
        :param tokens: [[2, 19, 27, 3, 0, 0], [2, 10, 3, 0, 0, 0]]
        :param return_special_tokens: 是否返回'<pad>', '<unk>', '<bos>', '<eos>'等特殊字符
        :param return_sentence: 返回的是一句话还是词序列
        :return: 由return_sentence决定，返回的是 '上课时学生手机响个不停‘, 还是 ['上课', '时', '学生', '手机', ’响个, '不停']
        """
        return [self.decode(index, return_special_tokens, return_sentence) for index in tokens]

    def padding(self, tokens: Union[map, Iterable[int], Iterable[Iterable[int]]], max_length: int, truncation=True, padding=True,
            padding_side='right', pad_begin_end=False):
        """
        :param tokens: [2, 19, 27, 3] 或 [[2, 19, 27, 3], [2, 10, 3]]
        :param max_length:
        :param truncation:
        :param padding:
        :param padding_side:
        :param pad_begin_end:
        :return:
        """
        if isinstance(tokens, map) or isinstance(tokens[0], Iterable):
            return batch_pad(tokens, max_length, truncation, padding, padding_side, pad_begin_end, self.pad, self.bos, self.eos)
        return pad(tokens, max_length, truncation, padding, padding_side, pad_begin_end, self.pad, self.bos, self.eos)

    def get_real_vocab(self):
        """
        :return: 除去特殊字符的词表
        """
        return self.vocab[len(self.reserved_token):]

    def save(self, path='vocab.txt', encoding=UTF8):
        with open(path, 'w', encoding=encoding) as f:
            f.write(self.SAVE_SEP.join([self.language, self.cut_type]) + '\n')
            f.write(self.SAVE_SEP.join(self.reserved_token) + '\n')
            f.write(self.SAVE_SEP.join(self.vocab))

    @classmethod
    def load(cls, path='vocab.txt', encoding=UTF8):
        with open(path, encoding=encoding) as f:
            lines = f.readlines()
        language, cut_type = lines[0].strip().split(Tokenizer.SAVE_SEP)
        return cls(vocab=lines[2].strip().split(Tokenizer.SAVE_SEP), reserved_token=lines[1].strip().split(Tokenizer.SAVE_SEP),
                        language=language, cut_type=cut_type)

    @classmethod
    def from_file(cls, file: str, encoding=UTF8, pattern='*', func=read_file, min_frequency=0, reserved_token=[], language='cn', cut_type='word',
            word_frequency=False):
        """
        :param file: 语料文件，可以是文件也可以是文件夹， 如：'./train.txt'. 如果是文件夹，会读取文件夹下的所有目录和文件.
        :param encoding: 编码
        :param pattern: 文件后缀，当file是文件夹的时候，会根据此后缀过滤文件
        :param func: 具体读取文件的处理函数，默认是read_file，可替换。注意：其函数签名为 function_name(path: str, encoding: str) -> corpus: Iterable[str]
        :param min_frequency: 最小词频，小于词词频的词会被忽略，默认是0，所有的词都保留
        :param reserved_token: 保留token, 如 '<pad>', '<unk>'等
        :param language: 语言 'cn'和'en'
        :param cut_type: 分词类型，只支持'word'和‘char'两种类型
        :param word_frequency: 是否统计词频
        """
        corpus = read_corpus_files(file, encoding, pattern, func)
        return cls(corpus=corpus, min_frequency=min_frequency, reserved_token=reserved_token, language=language, cut_type=cut_type,
                        word_frequency=word_frequency)

    @classmethod
    def from_corpus(cls, corpus: Iterable[str], min_frequency=0, reserved_token=[], language='cn', cut_type='word', word_frequency=False):
        """
        :param corpus: 语料，每个元素是一句话，如：['上课时学生手机响个不停，老师一怒之下把手机摔了。', '家长拿发票让老师赔', ....]
        :param min_frequency: 最小词频，小于词词频的词会被忽略，默认是0，所有的词都保留
        :param reserved_token: 保留token, 如 '<pad>', '<unk>'等
        :param language: 语言 'cn'和'en'
        :param cut_type: 分词类型，只支持'word'和‘char'两种类型
        :param word_frequency: 是否统计词频
        """
        return cls(corpus=corpus, min_frequency=min_frequency, reserved_token=reserved_token, language=language, cut_type=cut_type,
                        word_frequency=word_frequency)

    @classmethod
    def from_cut_corpus(cls, cut_corpus: Iterable[Iterable[str]], min_frequency=0, reserved_token=[], language='cn', cut_type='word', word_frequency=False):
        """
        :param cut_corpus: 分词后的语料，每个元素是一句话，如：[['上课', '时', '学生', '手机', '响', '个', '不停'], ['家长', '拿', '发票', '让', '老师', '赔']]
        :param min_frequency: 最小词频，小于词词频的词会被忽略，默认是0，所有的词都保留
        :param reserved_token: 保留token, 如 '<pad>', '<unk>'等
        :param language: 语言 'cn'和'en'
        :param cut_type: 分词类型，只支持'word'和‘char'两种类型
        :param word_frequency: 是否统计词频
        """
        return cls(cut_corpus=cut_corpus, min_frequency=min_frequency, reserved_token=reserved_token, language=language, cut_type=cut_type,
                        word_frequency=word_frequency)

    @classmethod
    def from_vocab(cls, vocab: Iterable[str], reserved_token=[]):
        """
        :param vocab: 词表，如：['上课', '学生', '手机', '不停', '，', '老师']
        :param reserved_token: 保留token, 如 '<pad>', '<unk>'等
        """
        return cls(vocab=vocab, reserved_token=reserved_token)

    def _get_token(self, indices: Iterable[int], return_special_tokens):
        if return_special_tokens:
            return [self.vocab[i] for i in indices]
        return [self.vocab[i] for i in indices if i not in [self.pad, self.bos, self.eos, self.unk]]

    def __len__(self):
        return self.vocab_size

    def __getitem__(self, index):
        return self.vocab[index]

    # def __call__(self, sentence: Union[str, Iterable[str]], max_length: int = None, truncation=True, padding=True, padding_side='right',
    #         pad_begin_end=False, keep_punctuation=False):
    #     return self.encode(sentence, max_length, truncation, padding, padding_side, pad_begin_end, keep_punctuation)


class Tokenizer(BaseTokenizer):
    """
    encode返回的是 {'input_ids': list} 或 {'input_ids': list, 'mask_ids': list}
    """

    def __init__(self, file: str = None, corpus: Iterable[str] = None, cut_corpus: Iterable[Iterable[str]] = None, vocab: Iterable[str] = None,
            min_frequency=0, reserved_token=[], language='cn', cut_type='word', word_frequency=False):
        """
        :param file: 语料文件， 如：'./train.csv'
        :param corpus: 语料，每个元素是一句话，如：['上课时学生手机响个不停，老师一怒之下把手机摔了。', '家长拿发票让老师赔', ...]
        :param cut_corpus: 语料，每个元素是是分词后的一句话，如：[['上课', '时', '学生', '手机', '响', '个', '不停'], ['家长', '拿', '发票', '让', '老师', '赔']]
        :param vocab: 词表，如：['上课', '学生', '手机', '不停', '，', '老师']
        :param min_frequency: 最小词频，小于词词频的词会被忽略，默认是0，所有的词都保留
        :param reserved_token: 保留token, 如 '<pad>', '<unk>'等
        :param language: 语言 'cn'和'en'
        :param cut_type: 分词类型，只支持'word'和‘char'两种类型
        :param word_frequency: 是否统计词频
        """
        super().__init__(file=file, corpus=corpus, cut_corpus=cut_corpus, vocab=vocab, min_frequency=min_frequency, reserved_token=reserved_token,
                         language=language, cut_type=cut_type, word_frequency=word_frequency)

    def encode_plus(self, sentence: Union[str, Iterable[str], Iterable[Iterable]], max_length: int = None, truncation=True, padding=True, padding_side='right',
            pad_begin_end=False, keep_punctuation=False, return_mask=False, is_split_into_words=False):
        """
        :param sentence: '上课时学生手机响个不停，老师一怒之下把手机摔了' 或 ['上课时学生手机响个不停，老师一怒之下把手机摔了。', '家长拿发票让老师赔', ....]
        :param max_length:
        :param truncation:
        :param padding:
        :param padding_side:
        :param pad_begin_end:
        :param keep_punctuation: 是否保留标点符号
        :param return_mask: 是否返回 mask_ids
        :param is_split_into_words: 是否已经分词
        :return:
        """
        if isinstance(sentence, str):
            if is_split_into_words:
                tokens = self.do_encode(sentence)
            else:
                tokens = cut(sentence, self.language, self.cut_type, keep_punctuation=keep_punctuation)
                tokens = self.do_encode(tokens)
            return self.padding_plus(tokens, max_length, truncation, padding, padding_side, pad_begin_end, return_mask)

        raise ValueError('参数"sentence"类型错误')

    def batch_encode_plus(self, sentences: Union[str, Iterable[str], Iterable[Iterable]], max_length: int = None, truncation=True, padding=True, padding_side='right',
            pad_begin_end=False, keep_punctuation=False, return_mask=False, is_split_into_words=False):
        """
        :param sentences: ['上课时学生手机响个不停，老师一怒之下把手机摔了。', '家长拿发票让老师赔', ....]
        :param max_length:
        :param truncation:
        :param padding:
        :param padding_side:
        :param pad_begin_end:
        :param keep_punctuation: 是否保留标点符号
        :param return_mask: 是否返回 mask_ids
        :param is_split_into_words: 是否已经分词
        :return:
        """
        if isinstance(sentences, Iterable):
            if is_split_into_words:
                tokens = map(self.do_encode, sentences)
            else:
                batch_cuts = batch_cut(sentences, language=self.language, cut_type=self.cut_type, keep_punctuation=keep_punctuation)
                tokens = map(self.do_encode, batch_cuts)
            return self.padding_plus(tokens, max_length, truncation, padding, padding_side, pad_begin_end, return_mask)

        raise ValueError('参数"sentence"类型错误')


    def padding_plus(self, tokens: Union[map, Iterable[int], Iterable[Iterable[int]]], max_length: int, truncation=True, padding=True,
            padding_side='right', pad_begin_end=False, return_mask=False):
        """
        :param tokens: [2, 19, 27, 3] 或 [[2, 19, 27, 3], [2, 10, 3]]
        :param max_length:
        :param truncation:
        :param padding:
        :param padding_side:
        :param pad_begin_end:
        :return:
        """
        if isinstance(tokens, map) or isinstance(tokens[0], Iterable):
            if return_mask:
                return batch_pad_mask(tokens, max_length, truncation, padding, padding_side, pad_begin_end, self.pad, self.bos, self.eos)
            return {'input_ids': batch_pad(tokens, max_length, truncation, padding, padding_side, pad_begin_end, self.pad, self.bos, self.eos)}

        if return_mask:
            return pad_mask(tokens, max_length, truncation, padding, padding_side, pad_begin_end, self.pad, self.bos, self.eos)
        return {'input_ids': pad(tokens, max_length, truncation, padding, padding_side, pad_begin_end, self.pad, self.bos, self.eos)}

    def __call__(self, sentence: Union[str, Iterable[str]], max_length: int = None, truncation=True, padding=True, padding_side='right',
            pad_begin_end=False, keep_punctuation=False, return_mask=False):
        return self.encode(sentence, max_length, truncation, padding, padding_side, pad_begin_end, keep_punctuation, return_mask)


class TokenEmbedding(Tokenizer):
    """
    可以传入已经训练好的embedding文件路径，也可以embedding数据, encode返回的是 {'input_ids': list} 或 {'input_ids': list, 'mask_ids': list}
    """

    def __init__(self, file: str = None, vocab: Iterable[str] = None, embedding: Iterable[Iterable[float]] = None, reserved_token=[],
            language='cn', cut_type='word', func=load_embedding, is_large_file=False):
        """
        :param file: embedding文件， 如：'./sgns.weibo.word.bz2'
        :param vocab: 词表，如：['上课', '学生', '手机', '不停', '，', '老师']，与embedding必须同时传入
        :param embedding: [[0.2548, -0.6879, 0.2578],[0.2548, -0.6879, 0.2578],[0.2548, -0.6879, 0.2578]]与vocab必须同时传入
        :param reserved_token: 保留token, 如 '<pad>', '<unk>'等
        :param language: 语言 'cn'和'en'
        :param cut_type: 分词类型，只支持'word'和‘char'两种类型
        :param func: 具体读取文件的处理函数，load_embedding，可替换。
               注意：其函数签名为 function_name(path: str, is_large_file: bool) -> (vocab: list[str], embedding: list[list[float]])
        :param is_large_file: 是否是大文件
        """
        if file:
            assert Path(file).is_file(), 'file必须是具体文件,不能是文件夹'
            vocab, embedding = func(file, is_large_file)
        elif not vocab or not embedding:
            raise ValueError('参数"path"为空的情况下，"vocab"和"embedding"不能为空.')
        super().__init__(vocab=vocab, reserved_token=reserved_token, language=language, cut_type=cut_type)
        reserved_token = self.reserved_token.copy()
        reserved_token.reverse()
        self.dim = len(embedding[0])
        for token in reserved_token:
            embedding = [[self.do_encode(token)] * self.dim] + embedding
        self.embedding = embedding

    @classmethod
    def from_file(cls, file: str, func=load_embedding, is_large_file=False, reserved_token=[], language='cn', cut_type='word'):
        """
        :param file: embedding文件， 如：'./sgns.weibo.word.bz2'. 注意：必须是单一文件，不能是文件夹。
        :param func: 具体读取文件的处理函数，load_embedding，可替换。注意：其函数签名为 function_name(path: str, is_large_file: bool) -> [vocab], [[embedding]]
        :param is_large_file: 是否是大文件
        :param reserved_token: 保留token, 如 '<pad>', '<unk>'等
        :param language: 语言 'cn'和'en'
        :param cut_type: 分词类型，只支持'word'和‘char'两种类型
        """
        return cls(file=file, reserved_token=reserved_token, language=language, cut_type=cut_type, func=func, is_large_file=is_large_file)

    @classmethod
    def from_vocab_embedding(cls, vocab: Iterable[str], embedding: Iterable[Iterable[float]], large_file=False, reserved_token=[], language='cn',
            cut_type='word'):
        """
        :param vocab: 词表，如：['上课', '学生', '手机', '不停', '，', '老师']
        :param embedding: [[0.2548, -0.6879, 0.2578],[0.2548, -0.6879, 0.2578],[0.2548, -0.6879, 0.2578]]
        :param large_file: 是否是大文件
        :param reserved_token: 保留token, 如 '<pad>', '<unk>'等
        :param language: 语言 'cn'和'en'
        :param cut_type: 分词类型，只支持'word'和‘char'两种类型
        """
        return cls(vocab=vocab, embedding=embedding, large_file=large_file, reserved_token=reserved_token, language=language, cut_type=cut_type)


if __name__ == '__main__':
    # file_name = './article.txt'
    # text = read_file(file_name)

    import pandas as pd
    import matplotlib.pyplot as plt

    DATA_PATH = r'D:\Study\kkb\代码实战课\week1\toutiao-text-classify\dataset\train.csv'
    # df = pd.read_csv(DATA_PATH)  # ['label']  ['sentence']

    # show_label_category_count(df['label'])
    # show_sentence_len_hist(df['sentence'], language='cn', cut_type='word', bins=50, scope=(0, 30))
    # show_token_frequency_plot(df['sentence'], language='cn', cut_type='word', scope=(0, 8000))

    # tokenizer = Tokenizer(corpus=df['sentence'].values, min_frequency=10, language='cn', cut_type='word')
    # tokenizer = BaseTokenizer.from_corpus(df['sentence'].values)
    # tokenizer.save()

    # sent = ('上课时学生手机响个不停，老师一怒之下把手机摔了，家长拿发票让老师赔，大家怎么看待这种事？', '老师一怒之下把手机摔了')
    # tokenizer = BaseTokenizer.load()
    # d = tokenizer.encode(sent, max_length=30, keep_punctuation=True, pad_begin_end=True)
    # print(d)
    # print(tokenizer.decode(d, return_special_tokens=False, return_sentence=True))
    # tokenizer = Tokenizer.load()
    # # print(type(tokenizer))
    # # # print(len(tokenizer))
    # # # print(tokenizer.vocab[:20])
    # # # print(tokenizer.reserved_token)
    # # # print(tokenizer.encode(['the', 'my']))
    # #
    # print(tokenizer.vocab[:20])
    # print(sent)
    # e = tokenizer(sent, max_length=30, keep_punctuation=True, pad_begin_end=True)
    # print(e)
    # d = tokenizer.decode(e)
    # print(d)

    # print(tokenizer.decode(d['input_ids'], return_special_tokens=False, return_sentence=True))
    # print(tokenizer.decode(d['input_ids']))

    # tk = [[101, 2198, 5125, 3198, 7313, 4764, 3221, 4507, 102, 7313, 4764, 3221, 4507, 102, 4764, 3221],
    #       [101, 2198, 5125, 3198, 7313, 4764, 3221, 4507, 102]]
    # r = tokenizer.padding(tk, max_length=15, truncation=True, padding_side='right', pad_begin_end=True)
    # print(r)

    # PATH = r'D:\Study\kkb\代码实战课\week1\toutiao-text-classify\dataset\sgns.weibo.word.bz2'
    # tokenizer = TokenEmbedding(PATH)
    # tokenizer = TokenEmbedding.from_file(PATH, is_large_file=False)
    # d = tokenizer.encode(sent, max_length=30, keep_punctuation=True, pad_begin_end=True)
    # print(d)
    # print(tokenizer.decode(d['input_ids'], return_special_tokens=False, return_sentence=True))
    # print(tokenizer.decode(d['input_ids']))
    #
    # tk = [[101, 2198, 5125, 3198, 7313, 4764, 3221, 4507, 102, 7313, 4764, 3221, 4507, 102, 4764, 3221],
    #       [101, 2198, 5125, 3198, 7313, 4764, 3221, 4507, 102]]
    # r = tokenizer.padding(tk, max_length=15, truncation=True, padding_side='right', pad_begin_end=True)
    # print(r)

    # print(batch_pad_mask(tk))

    # tokenizer = BaseTokenizer.from_file('./', pattern='*.txt', language='en')
    # print(tokenizer.vocab)

    # for f in get_files(r'D:\tmp'):
    #     print(f)

    for line in read_large_file('./article.txt'):
        print(line)

