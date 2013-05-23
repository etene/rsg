#!/bin/env python
# -*- coding: utf8 -*-
"""
	Random Sentence Generator
	Generates a random sentence based on the input file(s)
"""
#~ Copyright © 2000 Etienne Noss <etienne.noss@etu.unistra.fr>
#~ This work is free. You can redistribute it and/or modify it under the
#~ terms of the Do What The Fuck You Want To Public License, Version 2,
#~ as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

# Imports
import re
import random
import fileinput


# Constants
SENTENCE_ENDS = "!?."
SEPARATORS = ",/\.;"
SPACELESS = "'-"
SPECIALCHARS = SENTENCE_ENDS + SEPARATORS + SPACELESS


def main():
	"""I should split that into separate files"""
	# Créée la liste de couples de mots
	tokens = parse_file()
	# Génère aléatoirement une suite de mots
	seq = get_random_sequence(tokens)
	# L'affiche en tant que phrase
	print list_to_sentence(seq)


def parse_file():
	"""
	Creates a dictionnary associating 2-word tuples with their
	possible successors"""

	# TODO: handle other special chars
	regex = re.compile("([A-Za-zàâêéèîïôù]+|[" + SPECIALCHARS + "])")
	words = dict()
	lastlastword, lastword = None, None

	# Iterates over each line in the input file(s),
	# then over each word in that line
	for line in fileinput.input():
		for word in regex.findall(line):
			# Turn every word into lowercase so we don't have a separate entry
			# for Foo, foo and FOO
			word = word.lower()
			if lastword and lastlastword:
				words.setdefault( (lastlastword, lastword), [] ).append(word)
			lastlastword, lastword = lastword, word
	return words


def get_random_sequence(words, min_len = 3):
	"""Generate a random sequence of words until a setence ending character
	is found"""
	while True:
		(lastlastword, lastword) = random.choice(words.keys())
		w =  words[(lastlastword, lastword)]
		if len([a for a in w if a in SPECIALCHARS]) < len(w):
			break
	result = []

	# adds a random word, then a random word chosen among its successors,
	# and so forth
	while True:
		word = random.choice(words[(lastlastword, lastword)])

		result.append(word)
		lastlastword, lastword = lastword, word
		# if a sentence ending character is found, stop
		if word in SENTENCE_ENDS and len(result) >= min_len:
			break
	return result

def titlecaseword(w):
	return w[0].upper() + w[1:]

def list_to_sentence(word_list):
	"""Turns a word list into a more or less typographically correct sentence"""
	
	prev = word_list[0]
	resulting_string = titlecaseword(prev)
	
	for word in word_list[1:]:
		if word not in SPECIALCHARS and prev not in SPACELESS:
			# put spaces between words, except if they are not real words
			resulting_string += " "
		if prev in SENTENCE_ENDS:
			word = titlecaseword(word)
		resulting_string += word
		prev = word
	return resulting_string


if __name__ == "__main__":
	main()
