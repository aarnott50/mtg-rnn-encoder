#!/usr/bin/python
#coding: utf8

from sys import argv
from constants import Constants
import sys
import json
import codecs
from string import digits, ascii_uppercase, ascii_lowercase
from itertools import product

def readCardsFromFile(fileName):
    cardsJson = ''
    with codecs.open(fileName, encoding = 'utf-8') as fileHandle:
        fileContents = fileHandle.read()
        cardsJson = json.loads(fileContents)
    return cardsJson

def extractCreatures(cards):
    creatures = {}
    for cardKey in cards.keys():
        card = cards[cardKey]
        if 'power' in card:
            creatures[cardKey] = card
    return creatures

if len(argv) != 2:
    print >> sys.stderr, 'Usage: ' + argv[0] + ' fileName'
    exit(1)

script, fileName = argv

cards = readCardsFromFile(fileName)

creatures = extractCreatures(cards)

print json.dumps(creatures, indent = 4, sort_keys=True)
