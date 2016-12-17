# Random Sentence Generator

This script takes one or more input files (or standard input) and generates random sentences based on it.
It uses some sort of Markov Chain algorithm where each pair of consecutive words is associated with its possible successors.

### Usage
TThe most simple case is to just pass a text file to the -t option. It will read that file and print some random text based on its contents.

You can also use the -s option to save the parsed data to a state file that can be later restored by passing it to the -l option. This can be useful to avoid re-parsing large text files many times, which can be long.

The -n option controls the minimum word count. The program will stop generating random text when that minimum is reached AND a sentence-ending character is encountered.

```
usage: rsg.py [-h] [-n MIN_WORDS] [-q] [-t TEXTFILE [TEXTFILE ...]] [-l FILE]
              [-s FILE]

Generate random sentences from text

optional arguments:
  -h, --help            show this help message and exit
  -n MIN_WORDS, --min-words MIN_WORDS
                        Resulting sentence's minimum word count (default: 50)
  -q, --quiet           Don't output anything (default: False)
  -t TEXTFILE [TEXTFILE ...], --textfile TEXTFILE [TEXTFILE ...]
                        One or more (preferably large) text files to use as
                        input (default: None)
  -l FILE, --load FILE  Restore a file saved with --save (default: None)
  -s FILE, --save FILE  Save the inner state for later restoration, in order
                        to avoid re-parsing text files (default: None)
```

### Example
*Using the King James Version Bible (included in the repository) as input*
```
./rsg.py -t kjv12.txt -n 20
Like cheese? Thou hast slain him with your speeches. They shall eat, and went his way rejoicing.
```

*Using the 1958 French Constitution*
```
$ ./rsg.py -t const.txt
La délégation de vote des assemblées parlementaires, des séances supplémentaires pour permettre, le crédit et les modalités prévues par une loi organique votée dans les mêmes termes par les lois peuvent être modifiés par décret les crédits se rapportant aux services votés.
```

### Requirements
* Python 3
* A long enough text

### Where to find long text files
* The King James Version bible is included, it's a good start
* [Project Gutenberg](http://www.gutenberg.org/) has a lot of cool ebooks downloadable in text format

### Flaws
* Doesn't retain the words' case
* -s and -l can't be used simultaneously at the moment

### Future improvement
* Refine the regexs for better parsing

### License
See COPYING
