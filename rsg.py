#!/bin/env python
# -*- coding: utf8 -*-
"""Génère une phrase aléatoire à partir du texte passé en paramètre
ou par stdin"""
#~ Copyright © 2000 Etienne Noss <etienne.noss@etu.unistra.fr>
#~ This work is free. You can redistribute it and/or modify it under the
#~ terms of the Do What The Fuck You Want To Public License, Version 2,
#~ as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

# Imports
import re
import random
import fileinput


# Constantes
SENTENCE_ENDS = "!?."
SEPARATORS = ",/\.;"
SPACELESS = "'-"
SPECIALCHARS = SENTENCE_ENDS + SEPARATORS + SPACELESS


def main():
	"""Décomposé pour plus de lisbilité"""
	# Créée la liste de couples de mots
	tokens = parse_file()
	# Génère aléatoirement une suite de mots
	seq = get_random_sequence(tokens)
	# L'affiche en tant que phrase
	print list_to_sentence(seq)


def parse_file():
	"""Créée un tableau contenant pour chaque couple de mots une liste de mots
	pouvant les suivre"""

	# Reconnaît les mots et les caractères spéciaux séparément
	regex = re.compile("([A-Za-zàâêéèîïôù]+|[" + SPECIALCHARS + "])")
	words = dict()
	lastlastword, lastword = None, None

	# Parcourt chaque ligne du fichier puis chaque token de la ligne
	for line in fileinput.input():
		for word in regex.findall(line):
			# Met tout en minuscule pour pas créeer une entrée pour chaque
			# casse possible du mot
			word = word.lower()
			if lastword and lastlastword:
				words.setdefault( (lastlastword, lastword), [] ).append(word)
			lastlastword, lastword = lastword, word
	return words


def get_random_sequence(words, min_len = 3):
	"""Génère une liste de mots aléatoires jusqu'à trouver une fin de phrase
	Si le point est trouvé avant min_len on continue"""
	while True:
		(lastlastword, lastword) = random.choice(words.keys())
		w =  words[(lastlastword, lastword)]
		if len([a for a in w if a in SPECIALCHARS]) < len(w):
			break
	result = []

	# Prend un mot au hasard, puis prend un mot pouvant le suivre au hasard, etc
	while True:
		word = random.choice(words[(lastlastword, lastword)])

		result.append(word)
		lastlastword, lastword = lastword, word
		# Si on trouve une fin de phrase et qu'on a au moins la taille minimale
		# On s'arrête
		if word in SENTENCE_ENDS and len(result) >= min_len:
			break
	return result

def titlecaseword(w):
	return w[0].upper() + w[1:]

def list_to_sentence(word_list):
	"""Transforme une liste en phrase plus ou moins typographiquement juste"""
	
	prev = word_list[0]
	# premier mot en majuscule
	resulting_string = titlecaseword(prev)
	
	for word in word_list[1:]:
		if word not in SPECIALCHARS and prev not in SPACELESS:
			# on met des espaces entre les mots sauf si c'est pas des mots
			resulting_string += " "
		if prev in SENTENCE_ENDS:
			word = titlecaseword(word)
		resulting_string += word
		prev = word
	return resulting_string


if __name__ == "__main__":
	main()
