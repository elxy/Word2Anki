# Word2Anki
Save word to Anki.

# Usage

## Requirements

1. Anki & AnkiConnect [link](https://ankiweb.net/shared/info/2055492159)
2. A local dictionary (*.mdx) file
3. Install required packages: `apt install python3-hunspell`

## Setting in Anki

1. Open Anki and install the addon called AnkiConnect to Anki. And ** keep Anki open ** when you want to use this function
2. Add a deck named **Default**

## Usage

```
usage: Word2Anki.py [-h] [--no-morphology] [-d] [--mdx MDX [MDX ...]] word

positional arguments:
  word                 the word adding to anki

optional arguments:
  -h, --help           show this help message and exit
  --no-morphology      Disable morphology.
  --mdx MDX [MDX ...]  Dictionaries use to generate definition.
```

# Based on:

* [mmjang/mdict-query](https://github.com/mmjang/mdict-query)
* [valuex/GoldenDict2Anki](https://github.com/valuex/GoldenDict2Anki)
