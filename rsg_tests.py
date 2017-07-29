#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
import unittest
from rsg import *
from tempfile import NamedTemporaryFile
from os import unlink
from copy import deepcopy


class TestToken(unittest.TestCase):

    def test_hash(self):
        """Tokens with the same value must have identical hashes"""
        t1 = Token(None, "what")
        t2 = Token(None, "what")
        t3 = Token(None, "the")
        self.assertEqual(hash(t1), hash(t2))
        self.assertNotEqual(hash(t2), hash(t3))

    def test_equality(self):
        """Tokens with the same value must test equal, and other not"""
        t1 = Token(None, "bacon")
        t2 = Token(None, "bacon")
        t3 = Token(None, "eggs")
        self.assertEqual(t1, t2)
        self.assertNotEqual(t2, t3)
        self.assertFalse(t1 == object())

    def test_repr(self):
        """Token's repr() must be of the form <Classname('value')>"""
        word = Word(None, "mustélidé")
        period = SentenceEnd(None, ".")
        self.assertEqual(repr(word), "<Word('mustélidé')>")
        self.assertEqual(repr(period), "<SentenceEnd('.')>")

    def test_str(self):
        tok = Token(None, "félidé")
        self.assertEqual(str(tok), "félidé")


class TestScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = RandomSentenceGenerator.scanner

    def test_scan_lines(self):
        """The scanner must scan the right tokens from an iterable of lines"""
        lines = [u"Bonjour's ,  !",
                 u"ça va ???"
                 ]
        tokens = self.scanner.scan_lines(lines)
        self.assertEqual(tokens.__class__.__name__, "generator")
        tokens = list(tokens)
        self.assertEqual(len(tokens), 8)
        # supposedly matched tokens and their types
        expected_tokens = [
            (u"bonjour", Word),
            (u"'", SpaceLessPunctuation),
            (u"s", Word),
            (u",", Punctuation),
            (u"!", SentenceEnd),
            (u"ça", Word),
            (u"va", Word),
            (u"???", SentenceEnd)

        ]
        for (string, klass), token in zip(expected_tokens, tokens):
            self.assertEqual(str(token), string)
            self.assertIsInstance(token, klass)


class TestRandomSentenceGenerator(unittest.TestCase):

    blabla = """
        De do do do, de da da da
        Is all I want to say to you
        De do do do, de da da da
        Their innocence will pull me through
        De do do do, de da da da
        Is all I want to say to you
        De do do do, de da da da
        They're meaningless and all that's true
    """

    def setUp(self):
        self.rsg = RandomSentenceGenerator()
        self.rsg.feed(self.blabla.splitlines())

    def test_key_tuples(self):
        """The inner data's keys must be word pairs from the input text"""
        data = self.rsg._data
        self.assertIn((Word(None, "de"), Word(None, "do")), data)
        self.assertIn((Word(None, "do"), Word(None, "do")), data)
        self.assertIn((Word(None, "all"), Word(None, "i")), data)
        self.assertIn((Word(None, "that"), SpaceLessPunctuation(None, "'")),
                      data)
        self.assertIn((Word(None, "me"), Word(None, "through")), data)

    def test_successors(self):
        """A given word pair must have successors and they must be weighted"""
        data = self.rsg._data
        key = tuple((Word(None, "da"), Word(None, "da")))
        successors = data[key].copy()
        # these words must be after 'da da'
        self.assertIn(Word(None, "da"), successors)
        self.assertIn(Word(None, "is"), successors)
        self.assertIn(Word(None, "they"), successors)
        self.assertIn(Word(None, "their"), successors)
        # 'da' must have a greater weight than every other token
        da_count = successors.pop(Word(None, "da"))
        for i in successors.values():
            self.assertGreater(da_count, i)

    def test_save_n_load(self):
        """Must be able to save & load data to a file"""
        olddata = deepcopy(self.rsg._data)
        # Create a temporary data file and save to it
        with NamedTemporaryFile(delete=False) as tmp:
            self.rsg.save_data(tmp)

        try:
            # Load data from the file, replacing it
            with open(tmp.name, "rb") as tmp2:
                self.rsg.restore_data(tmp2, replace=True)
            # reloaded data must be the same
            self.assertEqual(self.rsg._data, olddata)
            # Must be able to restore without replacing
            with open(tmp.name, "rb") as tmp2:
                self.rsg.restore_data(tmp2)
                # TODO test
        finally:
            unlink(tmp.name)

    def test_get_sentences(self):
        """get_sentences must return text conforming to the passed params"""
        # Test a few times since the results are random
        for _ in range(10):
            # Default parameters: min_words=50, max_words=60
            text = self.rsg.get_sentences()
            self.assertGreater(len(text.split()), 49, "text is shorter than "
                               "the default minimum length")
            self.assertGreater(61, len(text.split()), "text is longer than "
                               "the default maximum length")

            # A whole lot of text: min_words=500, max_words must be 600
            text = self.rsg.get_sentences(min_words=500)
            self.assertGreater(len(text.split()), 499, "text is shorter than "
                               "the passed minimum length")
            self.assertGreater(601, len(text.split()), "text is longer than "
                               "the computed maximum length")

            # Only one word
            text = self.rsg.get_sentences(max_words=1)
            self.assertEqual(len(text.split()), 1, "Exactly one word expected")

            # Supplying only max_words should work as expected
            text = self.rsg.get_sentences(max_words=10)
            self.assertGreater(11, len(text.split()), "sentence is longer "
                               "than the maximum passed length")

            # Invalid parameters
            with self.assertRaises(ValueError):
                self.rsg.get_sentences(min_words=0)
            with self.assertRaises(ValueError):
                self.rsg.get_sentences(max_words=0)
            with self.assertRaises(ValueError):
                self.rsg.get_sentences(min_words=50, max_words=10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
