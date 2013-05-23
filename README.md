# Random Sentence Generator

This script takes one or more input files (or standard input) and generates random sentences based on it.
It uses some sort of Markov Chains algorithm where each pair of words is associated with its possible successors.

### Usage
```
python rsg.py [input file(s)] [-n minimum word count]
```

### Example
*Using the King James Version bible as input*
```
$python rsg.py kjv12.txt -n 20
Like cheese? Thou hast slain him with your speeches. They shall eat, and went his way rejoicing.
```

*Using the 1598 French Constitution*
```
$ python rsg.py const.txt
La délégation de vote des assemblées parlementaires, des séances supplémentaires pour permettre, le crédit et les modalités prévues par une loi organique votée dans les mêmes termes par les lois peuvent être modifiés par décret les crédits se rapportant aux services votés.
```

### Requirements
* Python 2.5+
* A long text

### Where to find long text files
* The King James Version bible is included, it's a good start
* [Project Gutemberg](http://www.gutenberg.org/) has a lot of cool ebooks downloadable in text format

### Flaws
* Doesn't handle special characters very well
* Doesn't retain the words' case


### License
See COPYING
