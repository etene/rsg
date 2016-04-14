#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Random Sentence Generator -- Surprisingly, generates random sentences"""

# Copyright © 2016 Etienne Noss
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

from re import Scanner as ReScanner, UNICODE
from collections import Counter, deque
import random
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType


class Token(object):
    """A token, matched by the regular expression scanner."""
    # The regex to match against
    RE = r""

    def __init__(self, _, value):
        """Creates the token with value.
        The re module's Scanner class passes its instance as the second
        argument, but we don't need it.
        """
        self.value = value

    def __str__(self):
        return self.value

    def __hash__(self):
        """The token's value hash"""
        return hash(self.value)

    def __repr__(self):
        return "<{s.__class__.__name__}('{s.value}')>".format(s=self)

    def __eq__(self, other):
        assert isinstance(other, self.__class__)
        return self.value == other.value


class Word(Token):
    """A simple word"""
    RE = r"\w+"


class Punctuation(Token):
    """One or more regular punctuation characters"""
    RE = r"[,:;]+"


class SpaceLessPunctuation(Punctuation):
    """A punctuation character which must not be surrounded with spaces"""
    RE = r"[-']"


class SentenceEnd(Punctuation):
    """A punctuation character which marks the end of a sentence"""
    RE = r"[!?\.]+"

# A list of the token types defined above
TOKEN_TYPES = [Word, Punctuation, SpaceLessPunctuation, SentenceEnd]


class Scanner(ReScanner):
    """A subclass of re's Scanner, with an added method to ease
    scanning from a file-like object.
    """
    def scan_lines(self, source):
        """Scans each line in the given iterable and yield its tokens"""
        for line in source:
            for token in self.scan(line.lower())[0]:
                yield token


class RandomSentenceGenerator(object):

    """
    The data used to generate sentences is represented as a hash table;
    its keys are tuples of KEY_SIZE tokens and its values are weighted
    lists of possible successors for the key. Assuming KEY_SIZE is 2,
    this could be one of the hash table's entries :
    ('hello', 'every'): {'body': 3, 'one': 1}

    The get_tokens method can then be called to get a semi random succession
    of tokens.
    """

    KEY_SIZE = 2

    # The scanner takes a list of (regex, callback) tuples
    scanner = Scanner([(t.RE, t) for t in TOKEN_TYPES] + [(r"[ ]+", None)],
                      UNICODE)

    def __init__(self):
        self.data = {}
        self._token_cache = {}
        self._key_cache = []

    def feed(self, iterable):
        """Feed an iterable (yielding lines of text)"""
        # FIFO queue containing the last KEY_SIZE tokens
        last_tokens = deque(maxlen=self.KEY_SIZE)

        # Scan each line, yielding tokens
        for token in self.scanner.scan_lines(iterable):
            # get the token from the cache or add it if nonexistent
            token = self._token_cache.setdefault(token, token)

            if len(last_tokens) == self.KEY_SIZE:
                # add the current token as a possible successor to the last tokens
                # XXX: should use a specialized counter that divides totals
                #      by the gcd() on update
                self.data.setdefault(tuple(last_tokens),
                                     Counter()).update((token,))
            last_tokens.append(token)

        # update the key cache
        self._key_cache = list(self.data.keys())

    def get_tokens(self):
        """Returns a generator that yields randomly selected tokens"""
        key = deque(random.choice(self._key_cache), maxlen=self.KEY_SIZE)
        while True:
            weighted_successors = []
            # TODO optimize this
            # lame weighted-random implementation
            for token, weight in self.data[tuple(key)].items():
                weighted_successors.extend(token for i in range(weight))

            yield key.popleft()
            key.append(random.choice(weighted_successors))

    def get_sentence(self, min_words=50):
        """Returns a sentence of at least 'min_words' words"""

        # Get a generator that returns tokens
        tokens = self.get_tokens()
        # Set to True every time a sentence-ending token is found
        capitalize = True
        sentence = []

        while True:
            # Get the next token
            token = next(tokens)
            # If we are at the beginning of a sentence and the current token
            # is a punctuation character, skip it. It wouldn't make sense and
            # would look weird.
            if capitalize and isinstance(token, Punctuation):
                continue

            word = token.value
            if capitalize:
                # We are at the beginning of a sentence;
                # capitalize the current word, and reset the flag
                word = word.capitalize()
                capitalize = False
            else:
                # If we are at the end of a sentence,
                # set the flag to capitalize the next word.
                capitalize = isinstance(token, SentenceEnd)

            # If the current token is a punctuation character,
            # pop the last space because there must be no spaces before it.
            if isinstance(token, Punctuation) and sentence[-1].isspace():
                sentence.pop()

            # Add the current token to the sentence
            sentence.append(word)

            # Add a space except if the current token doesn't need one
            if not isinstance(token, SpaceLessPunctuation):
                sentence.append(' ')

            # If we are at the end of a sentence and we've reached the
            # required word count, we can return.
            if capitalize and len(sentence) >= min_words:
                break

        return ''.join(sentence)


def main():
    psr = ArgumentParser(description="Generate random sentences from text",
                         formatter_class=ArgumentDefaultsHelpFormatter)
    psr.add_argument("-n", "--min-words", type=int, default=50,
                     help="resulting sentence's minimum word count")
    psr.add_argument("textfile", type=FileType("r"), nargs="+",
                     help="One or more (preferably large) text files "
                          "to use as input")
    args = psr.parse_args()

    gen = RandomSentenceGenerator()
    for txt in args.textfile:
        gen.feed(txt)
    print(gen.get_sentence(args.min_words))


if __name__ == '__main__':
    main()
