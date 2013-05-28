# Random Sentence Generator

This script takes one or more input files (or standard input) and generates random sentences based on it.
It uses some sort of Markov Chain algorithm where each pair of consecutive words is associated with its possible successors.

### Usage
The -n option controls the minimum word count. The program will stop generating random text when that minimum is reached AND a sentence-ending character is encountered.
If no files are given as parameters, it reads from stdin, which means you can pipe another program's input or use shell redirection.
```
python rsg.py [input file(s)] [-n minimum word count]
```

### Example
*Using the King James Version Bible (included in the repository) as input*
```
$python rsg.py kjv12.txt -n 20
Like cheese? Thou hast slain him with your speeches. They shall eat, and went his way rejoicing.
```

*Using the 1958 French Constitution*
```
$ python rsg.py const.txt
La délégation de vote des assemblées parlementaires, des séances supplémentaires pour permettre, le crédit et les modalités prévues par une loi organique votée dans les mêmes termes par les lois peuvent être modifiés par décret les crédits se rapportant aux services votés.
```

### Requirements
* Python 2.5+ (to be honest, only tested in 2.6 and 2.7)
* A long enough text

### Where to find long text files
* The King James Version bible is included, it's a good start
* [Project Gutenberg](http://www.gutenberg.org/) has a lot of cool ebooks downloadable in text format

### Flaws
* Doesn't handle special characters very well
* Doesn't retain the words' case
* Parses the whole file at each run


### License
See COPYING
