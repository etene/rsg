#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods

"""Random Sentence Generator -- Generates pseudo-random sentences from text"""

# Copyright © Etienne Noss
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

from re import Scanner as ReScanner, UNICODE
from collections import Counter, deque, defaultdict
import random
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
import pickle


class Token(object):
    # pylint: disable=invalid-name
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
        if not isinstance(other, self.__class__):
            return NotImplemented
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

    The get_tokens method can then be called to get a semi random
    succession of tokens.
    """

    KEY_SIZE = 2

    # The scanner takes a list of (regex, callback) tuples
    scanner = Scanner([(t.RE, t) for t in TOKEN_TYPES] + [(r"[ ]+", None)],
                      UNICODE)

    def __init__(self):
        # Every function that modifies self._data
        # must call _update_key_cache() afterwards
        self._data = defaultdict(Counter)
        self._key_cache = []

    def _update_key_cache(self):
        """Call when you're done modifying self._data.
        We store key cache so we don't have to call self._data.keys()
        (which is expensive) every time we need its keys."""
        self._key_cache = list(self._data)

    def feed(self, iterable):
        """Feed an iterable (yielding lines of text)"""
        # FIFO queue containing the last KEY_SIZE tokens
        last_tokens = deque(maxlen=self.KEY_SIZE)

        # Scan each line, yielding tokens
        for token in self.scanner.scan_lines(iterable):
            # add the token to the cache it if nonexistent
            if len(last_tokens) == self.KEY_SIZE:
                # add current token as a possible successor to the last one
                # XXX: should use a specialized counter that divides totals
                #      by the gcd() on update
                key = tuple(last_tokens)
                self._data[key].update((token,))
            last_tokens.append(token)
        self._update_key_cache()

    def restore_data(self, filep, replace=False):
        """Restores data previously saved to disk with save_data().
        If replace evaluates to True, replaces any existing data,
        else updates it as if it were parsed.
        """
        loaded = pickle.load(filep)
        if replace or not self._data:
            self._data = loaded
        else:
            for key, value in loaded.items():
                self._data[key].update(value)
        self._update_key_cache()

    def save_data(self, filep):
        """Saves the data to a pickle-format file for later restoration."""
        pickle.dump(self._data, filep)

    def _get_random_key(self):
        """Returns a key randomly chosen from self._data"""
        return deque(random.choice(self._key_cache), maxlen=self.KEY_SIZE)

    def get_tokens(self):
        """Returns a generator that yields randomly selected tokens"""
        key = self._get_random_key()
        while True:
            weighted_successors = []
            # TODO optimize this
            # lame weighted-random implementation
            for token, weight in self._data[tuple(key)].items():
                weighted_successors.extend(token for i in range(weight))
            yield key.popleft()
            # If there were successors for this key,
            # choose one of them to update it
            if weighted_successors:
                key.append(random.choice(weighted_successors))
            else:
                # That means there were no successors: choose a random key
                key = self._get_random_key()

    @staticmethod
    def _validate_min_max(min_words, max_words):
        """Validate & set values for min_words & max_words, according to
        get_sentences() docstring"""
        default_min = False
        if min_words is None:
            # Default value for min_words
            min_words = 50
            default_min = True
        elif min_words <= 0:
            raise ValueError("'min_words' must be greater than 0")
        if max_words is None:
            # Default value for max_words
            max_words = int(min_words * 1.2)
        elif max_words <= 0:
            raise ValueError("'max_words' must be greater than 0")
        elif max_words < min_words:
            # If only max_words was supplied and it's smaller than min_words,
            # override min_words
            if default_min is True:
                min_words = max_words
            else:
                raise ValueError("'max_words' must be greater"
                                 "than 'min_words'")
        return min_words, max_words

    def get_sentences(self, min_words=None, max_words=None):
        """Returns text of at least 'min_words' and at most 'max_words'.

        The text generation stops when it encounters a sentence-ending token
        and the current text is at least 'min_words' long, or if the generated
        text reaches 'max_words' in length.

        The default value for 'min_words' is 50.
        The default for 'max_words' is 'min_words' * 1.2.
        """

        # Validate params
        min_words, max_words = self._validate_min_max(min_words, max_words)
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
            joined_sentence = "".join(sentence)
            slen = len(joined_sentence.split())
            if (capitalize and slen >= min_words) or slen == max_words:
                return joined_sentence


def main():
    psr = ArgumentParser(description="Generate random sentences from text",
                         formatter_class=ArgumentDefaultsHelpFormatter)
    psr.add_argument("-n", "--min-words", type=int, default=50,
                     help="Resulting sentence's minimum word count")
    psr.add_argument("-q", "--quiet", default=False, action="store_true",
                     help="Don't output anything")
    psr.add_argument("-t", "--textfile", type=FileType("r"), nargs="+",
                     help="One or more (preferably large) text files "
                          "to use as input")
    psr.add_argument("-l", "--load", type=FileType("rb"), metavar="FILE",
                     help="Restore a file saved with --save")
    psr.add_argument("-s", "--save", type=FileType("wb"), metavar="FILE",
                     help="Save the inner state for later restoration, "
                          "in order to avoid re-parsing text files")

    args = psr.parse_args()
    if not (args.load or args.textfile):
        psr.error("Provide at least a database file to load (-l/--load) "
                  "or a text file (-t/--textfile).")

    gen = RandomSentenceGenerator()

    # Restore pickled data
    if args.load:
        gen.restore_data(args.load)

    # Read one or more text files
    if args.textfile:
        for txt in args.textfile:
            gen.feed(txt)

    # Print a generated sentence
    if not args.quiet:
        print(gen.get_sentences(args.min_words))

    # Pickle the data
    if args.save:
        gen.save_data(args.save)


if __name__ == '__main__':
    main()
