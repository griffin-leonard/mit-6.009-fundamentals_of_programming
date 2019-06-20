# -*- coding: utf-8 -*-

import re
import random
import string

TITLES = r"(mr|mrs|ms|dr)[.]"
ABBREVIATIONS = r"([a-z][.][a-z][.](?:[a-z][.])*)"
OTHERS = r'(ph\.d\.|e\.g\.|i\.e\.|\.\.\.)'
URLS = r'(https?:\/\/)?([a-z0-9_\-]+\.)?[a-z0-9_\-]+\.[a-z0-9_\-]+'
SYMBOL_CHARS = string.ascii_letters + string.digits


def clear_punctuation(x):
    """
    Remove punctuation from a given string.
    """
    for i in '‘’“”"\'.!?{}()[]-_+=~`@#$%^&*,;:':
        x = x.replace(i, '')
    return x


def deunicode(x):
    """
    Replace unicode 'smart quotes' with quotes or asterisks, and delete all
    other non-ascii characters
    """
    for i in '‘’':
        x = x.replace(i, "'")
    for i in "“”":
        x = x.replace(i, '"')
    return re.sub(r'[^\x00-\x7F]+','', x)


def make_symbol(length=10):
    """
    Generate a random sequence of the given length
    """
    return '<%s>' % ''.join(tuple(random.choice(SYMBOL_CHARS) for _ in range(length)))


def gensyms(names, text):
    """
    Helper.  Generate symbols for the given strings, making sure each generated
    symbol is unique and does not appear in the input text.
    """
    out = {}
    for n in names:
        sym = None
        while sym is None or sym in out.values() or sym in text:
            sym = make_symbol()
        out[n] = sym
    return out


def tokenize_sentences(text, remove_punctuation=True):
    """
    Split a piece of text into sentences.

    This is not a perfect implementation, but it does a few things to try to be
    smart about breaking at sentences, and avoiding things like mr. and mrs.
    being treated as ends of sentences.
    """
    # generate symbols to replace punctuation
    # create forward and reverse lookups for them
    punctuation = '.?!'
    encoded_punctuation = gensyms(list(punctuation) + ['STOP'], text)

    # replace weird unicode quotes, replace line breaks with spaces, lowercase
    text = re.sub(r'\s+', ' ', deunicode(text.lower()))

    # replace titles, abbreviations, etc, with versions with no periods
    for check in (TITLES, ABBREVIATIONS, OTHERS, URLS):
        text = re.sub(check, lambda m: m.group(0).replace('.', encoded_punctuation['.']), text)

    # mark remaining punctuation as ends of sentences
    for punct in punctuation:
        text = text.replace(punct, '%s%s' % (punct, encoded_punctuation['STOP']))

    # now, re-set punctuation we replaced earlier
    for punct in punctuation:
        text = text.replace(encoded_punctuation[punct], punct)

    # strip extra whitespace, and, if necessary, clear punctuation
    out = [i for i in text.split(encoded_punctuation['STOP'])]
    if remove_punctuation:
        out = [' '.join(clear_punctuation(i).split()) for i in out]
    return [j for j in (i.strip() for i in out) if j]
