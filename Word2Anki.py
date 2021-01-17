# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 00:00:15 2019

@ori_author: valuex
@author: elxy
"""

import argparse
import json
import logging
import re
import sys
import urllib.request

import hunspell
from mdict_query import IndexBuilder

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def NoteContent(FrontStr, BackStr):
    BackStr = BackStr.replace('"', '\\"')
    BackStr = BackStr.replace(u'\xa0', u' ')
    BackStr = re.sub(r'<img.*?>', '', BackStr)
    newnote = """
    {
        "deckName": "Default",
        "modelName": "Basic",
        "fields": {
            "Front": "%s",
            "Back": "%s"
        },
        "options": {
            "allowDuplicate": false
        },
        "tags": [ ]
    }
    """ % (FrontStr, BackStr)

    return newnote


def search_word_in_dict(word: str, dict: str, morphology: bool = True):
    global logger

    word = word.strip(' \n')
    words = [word]
    if morphology:
        hobj = hunspell.HunSpell('/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')
        if hobj.spell(word) and hobj.stem(word):
            words = [b.decode() for b in hobj.stem(word)]
            logger.debug('Get stems: {}.'.format(', '.join(words)))

    builder = IndexBuilder(dict)
    builder.check_build()
    for w in words:
        meanings = builder.mdx_lookup(w, ignorecase=True)
        if not meanings:
            continue
        logger.debug('Find {} meanings of word {} from dictionary {}.'.format(len(meanings), w, dict))
        if w != word:
            word = w
        return word, meanings[0]
    logger.debug('Cannot find word {} from dictionary {}.'.format(word, dict))
    return word, None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('word', help='the word adding to anki')
    parser.add_argument('--no-morphology', dest='morphology', action='store_false', help='Disable morphology.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug information.')
    parser.add_argument('--mdx',
                        nargs='+',
                        default=['CALD4.mdx', 'WordNet 3.0.mdx'],
                        help='Dictionaries use to generate definition.')
    args = vars(parser.parse_args())

    if args['debug']:
        logger.setLevel(logging.DEBUG)

    for mdx in args['mdx']:
        word, record = search_word_in_dict(args['word'], mdx, args['morphology'])
        if record:
            break
    if not record:
        logger.error('Cannot find word {} in dictionaries {}.'.format(word, ', '.join(args['mdx'])))
        sys.exit(1)

    cardnote = NoteContent(word, record)
    newnote = json.loads(cardnote, strict=False)
    try:
        result = invoke('addNote', note=newnote)
    except Exception as err:
        logger.error('Cannot add note of {}: {}.'.format(word, err))
        sys.exit(1)
    logger.info('Succed to add word {} to anki.'.format(word))
