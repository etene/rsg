#!/bin/env python
# -*- coding: utf8 -*-
"""Random Sentence Generator -- Generates random sentences (duh)"""

#~ Copyright © 2013 Etienne Noss <etienne.noss@etu.unistra.fr>
#~ This work is free. You can redistribute it and/or modify it under the
#~ terms of the Do What The Fuck You Want To Public License, Version 2,
#~ as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.


# Imports
import re
import random
import fileinput
import sys


# Constants
SENTENCE_ENDS = "!?."	# Characters that may end a sentence
SEPARATORS = ",/\.;"	# Characters that may separate words
SPACELESS = "'-"		# Characters that must'nt be surrounded with spaces
SPECIALCHARS = SENTENCE_ENDS + SEPARATORS + SPACELESS
DEFAULT_MIN_WORDS = 10	# Default minimum word count


# Functions
def main():
	"""I should split that into separate files"""
	
	if "-h" in sys.argv: # Print help and exit
		print "usage: %s [input file(s)] [-n minimum word count]" % sys.argv[0]
		sys.exit(0)
	
	min_words = DEFAULT_MIN_WORDS
	if "-n" in sys.argv: # Parse the minimum word count
		try:
			min_words = int(sys.argv.pop(sys.argv.index("-n")+1))
		except IndexError:
			print "Option -n requires an argument (the minimum word count)."
		except ValueError:
			print "Invalid argument to -n (give it the minimum word count)."
		sys.argv.remove("-n")
	
	# Create the word dictionnary
	tokens = parse_file()
	
	try: # Generate a word sequence
		seq = get_random_sequence(tokens, min_words)
	except IndexError:
		print "There seems to be an insufficient number of words in your input."
		sys.exit(1)
	
	# Print it
	print list_to_sentence(seq)


def parse_file():
	"""Create a dictionnary associating 2-word tuples with their
	possible successors"""
	
	# TODO: handle other special chars
	regex = re.compile("([A-Za-zàâêéèîïôù€$£&]+|[" + SPECIALCHARS + "])")
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
				words.setdefault((lastlastword, lastword), []).append(word)
			lastlastword, lastword = lastword, word
	return words


def get_random_sequence(words, min_len=50):
	"""Generate a random sequence of words of at least min_len characters
	until a sentence ending character is found"""
	
	while True:
		(lastlastword, lastword) = random.choice(words.keys())
		if lastlastword not in SPECIALCHARS:
			break
	result = [lastlastword, lastword]

	# Adds a random word, then a random word chosen among its successors,
	# and so forth.
	while True:
		word = random.choice(words[(lastlastword, lastword)])
		result.append(word)
		lastlastword, lastword = lastword, word
		# if a sentence ending character is found, stop
		if word in SENTENCE_ENDS and len(result) >= min_len:
			break
	return result


def list_to_sentence(word_list):
	"""Turns a word list into a more or less typographically correct sentence"""
	
	# Start the sentence with a title case word
	resulting_string = previous_word = word_list[0].title()
	for word in word_list[1:]:
		if word not in SPECIALCHARS and previous_word not in SPACELESS:
			# Put spaces between words, except if they are not real words
			resulting_string += " "
		if previous_word in SENTENCE_ENDS:
			# If the previous word ended a sentence, titlecase this one
			word = word.title()
		resulting_string += word
		previous_word = word
	return resulting_string


if __name__ == "__main__":
	main()
