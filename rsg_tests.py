#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
import unittest
from rsg import *


class TestToken(unittest.TestCase):

    def test_hash(self):
        """Tokens with the same value must have identical hashes"""
        t1 = Token(None, "what")
        t2 = Token(None, "what")
        t3 = Token(None, "the")
        self.assertEqual(hash(t1), hash(t2))
        self.assertNotEqual(hash(t2), hash(t3))

    def test_equality(self):
        """Tokens with the same value must test equal"""
        t1 = Token(None, "bacon")
        t2 = Token(None, "bacon")
        t3 = Token(None, "eggs")
        self.assertEqual(t1, t2)
        self.assertNotEqual(t2, t3)

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
        lines = ["Bonjour's ,  !",
                 "ça va ???"
                 ]
        tokens = self.scanner.scan_lines(lines)
        self.assertEqual(tokens.__class__.__name__, "generator")
        tokens = list(tokens)
        self.assertEqual(len(tokens), 8)
        # supposedly matched tokens and their types
        expected_tokens = [
            ("bonjour", Word),
            ("'", SpaceLessPunctuation),
            ("s", Word),
            (",", Punctuation),
            ("!", SentenceEnd),
            ("ça", Word),
            ("va", Word),
            ("???", SentenceEnd)

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
        data = self.rsg.data
        self.assertIn((Word(None, "de"), Word(None, "do")), data)
        self.assertIn((Word(None, "do"), Word(None, "do")), data)
        self.assertIn((Word(None, "all"), Word(None, "i")), data)
        self.assertIn((Word(None, "that"), SpaceLessPunctuation(None, "'")), data)
        self.assertIn((Word(None, "me"), Word(None, "through")), data)

    def test_successors(self):
        """A given word pair must have successors and they must be weighted"""
        data = self.rsg.data
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

if __name__ == '__main__':
    unittest.main(verbosity=2)

