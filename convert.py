#!/usr/bin/python
#coding: utf8

from sys import argv
from constants import Constants
import sys
import json
import codecs
from string import digits, ascii_uppercase, ascii_lowercase
from itertools import product

class TokenizerState:
    START, SINGLE_CHARACTER, WORD, CURLY1, CURLY2, CURLY3 = range(6)

class Tokenizer:
    SINGLE_CHARACTERS = u' :;/.",()‘—\n\r\t'
    CURLY_CHARACTER_START = u'{'
    CURLY_CHARACTER_END = u'}'

    def scan(self, text):
        if not text:
            return []

        tokens = []
        tokenStartIndex = 0
        index = 0
        state = TokenizerState.START
        while index < len(text):
            nextState = self.getStateTransition(state, text[index:index + 1])
            if nextState is None:
                tokens.append(text[tokenStartIndex:index])
                tokenStartIndex = index
                state = TokenizerState.START
            else:
                state = nextState
                index = index + 1

        tokens.append(text[tokenStartIndex:index])

        return tokens


    def getStateTransition(self, state, character):
        if state == TokenizerState.START:
            if character in Tokenizer.SINGLE_CHARACTERS:
                return TokenizerState.SINGLE_CHARACTER
            elif character in Tokenizer.CURLY_CHARACTER_START:
                return TokenizerState.CURLY1
            else:
                return TokenizerState.WORD
        elif state == TokenizerState.SINGLE_CHARACTER:
            return None
        elif state == TokenizerState.WORD:
            if character in Tokenizer.SINGLE_CHARACTERS:
                return None
            elif character in Tokenizer.CURLY_CHARACTER_START:
                return None
            else:
                return TokenizerState.WORD
        elif state == TokenizerState.CURLY1:
            return TokenizerState.CURLY2
        elif state == TokenizerState.CURLY2:
            if character in Tokenizer.CURLY_CHARACTER_START:
                return None
            elif character in Tokenizer.CURLY_CHARACTER_END:
                return TokenizerState.CURLY3
            else:
                return TokenizerState.CURLY2
        elif state == TokenizerState.CURLY3:
            return None
        else:
            print '???'
            sys.exit(2)

def generateDictionaryEncodings():
    dictionaryEncodings = []
    chars = digits + ascii_uppercase + ascii_lowercase
    for n in range(1, Constants.MAX_ENCODING_CHARACTERS + 1):
        for comb in product(chars, repeat = n):
            dictionaryEncodings.append(''.join(comb))
    return dictionaryEncodings

def readCardsFromFile(fileName):
    cardsJson = ''
    with codecs.open(fileName, encoding = 'utf-8') as fileHandle:
        fileContents = fileHandle.read()
        cardsJson = json.loads(fileContents)
    return cardsJson

def replaceCardNameWithTHIS(cards):
    for card in cards.values():
        if 'text' in card:
            card['text'] = card['text'].replace(card['name'], '$THIS')

def createEncodingAndDecodingDictionaries(cards):
    uniqueTokens = getAllUniqueTokens(cards)

    sortedUniqueTokens = list(uniqueTokens)
    sortedUniqueTokens.sort()

    encodingDictionary = {}
    decodingDictionary = {}
    for token in sortedUniqueTokens:
        dictionaryKey = ''
        if len(token) == 1 and 32 <= ord(token) and ord(token) <= 47:
            dictionaryKey = token
        elif len(token) == 1 and ord(token) == 10:
            dictionaryKey = '~'
        else:        
            dictionaryKey = dictionaryEncodings.pop()
        dictionaryValue = token
        decodingDictionary[dictionaryKey] = dictionaryValue
        encodingDictionary[dictionaryValue] = dictionaryKey
    return (encodingDictionary, decodingDictionary)

def getAllUniqueTokens(cards):
    allUniqueTokens = set()
    for card in cards.values():
        allUniqueTokens = allUniqueTokens | set(getTokensForCard(card))
    return allUniqueTokens

def getTokensForCard(card):
    tokens = []
    tokens.extend(getTokensForCardField(card, 'name'))
    tokens.extend(getTokensForCardField(card, 'manaCost'))
    tokens.extend(getTokensForCardField(card, 'type'))
    tokens.extend(getTokensForCardField(card, 'text'))
    tokens.extend(getTokensForCardField(card, 'power'))
    tokens.extend(getTokensForCardField(card, 'toughness'))
    return tokens

def getTokensForCardField(card, fieldName):
    tokenizer = Tokenizer()
    if fieldName in card:
        return tokenizer.scan(card[fieldName])
    else:
        return []



def writeDictionaryAsJsonToFile(dictionary, fileName):
    with codecs.open(fileName, mode='w', encoding='utf-8') as fileHandle:
        json.dump(dictionary, fileHandle, sort_keys=True, indent = 4)

def getFormattedCard(card, encodingDictionary):
        cardFields = []        
        if 'name' in card:
            tokens = getTokensForCardField(card, 'name')            
            cardFields.append(getEncodedTokenString(tokens, encodingDictionary))
        if 'manaCost' in card:
            tokens = getTokensForCardField(card, 'manaCost')            
            cardFields.append(getEncodedTokenString(tokens, encodingDictionary))
        if 'type' in card:
            tokens = getTokensForCardField(card, 'type')            
            cardFields.append(getEncodedTokenString(tokens, encodingDictionary))
        if 'text' in card:
            tokens = getTokensForCardField(card, 'text')            
            cardFields.append(getEncodedTokenString(tokens, encodingDictionary))
        if 'power' in card and 'toughness' in card:
            powerTokens = getTokensForCardField(card, 'power')            
            toughnessTokens = getTokensForCardField(card, 'toughness')
            cardFields.append(getEncodedTokenString(powerTokens, encodingDictionary) + encodingDictionary['/'] + getEncodedTokenString(toughnessTokens, encodingDictionary))
        return Constants.SECTION_SEPARATOR.join(cardFields)
    
def getEncodedTokenString(tokens, encodingDictionary):
    encodedTokens = []
    for token in tokens:
        encodedTokens.append(encodingDictionary[token])
    return ''.join(encodedTokens)

######################################################################

if len(argv) != 4:
    print >> sys.stderr, 'Usage: ' + argv[0] + ' fileName, encodingDictionaryFileName, decodingDictionaryFileName'
    exit(1)

script, fileName, encodingDictionaryFileName, decodingDictionaryFileName = argv

dictionaryEncodings = generateDictionaryEncodings()
dictionaryEncodings.reverse()

cards = readCardsFromFile(fileName)

replaceCardNameWithTHIS(cards)

encodingDictionary, decodingDictionary = createEncodingAndDecodingDictionaries(cards)

writeDictionaryAsJsonToFile(encodingDictionary, encodingDictionaryFileName)
writeDictionaryAsJsonToFile(decodingDictionary, decodingDictionaryFileName)

for card in cards.values():
    print getFormattedCard(card, encodingDictionary).encode('utf-8')
