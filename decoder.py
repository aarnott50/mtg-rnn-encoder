#!/usr/bin/python
#coding: utf8

from sys import argv
from constants import Constants
import sys
import json
import codecs

def breakSectionIntoTokens(section, decodingDictionary):
    tokens = []
    currentToken = ''
    currentIndexStart = 0
 
    token = ''
    currentIndexEnd = 1
    while len(section) > 0:
        token = token + section[0]
        section = section[1:]
        if token not in decodingDictionary and token != '\n':
            tokens.append(''.join(token[:-1]))
            token = token[-1]

    tokens.append(token)    

    return tokens

###################################################

script, decodingDictionaryFileName, decodingTargetFileName = argv

decodingDictionary = None
with codecs.open(decodingDictionaryFileName, encoding='utf-8') as fileHandle:
    fileContents = fileHandle.read()
    decodingDictionary = json.loads(fileContents)

with codecs.open(decodingTargetFileName, encoding='utf-8') as fileHandle:
    lines = fileHandle.readlines()
    for line in lines:
        splitLine = line.split(Constants.SECTION_SEPARATOR)

        decodedSections = []
        for section in splitLine:
            decodedTokenText = ''
            tokens = breakSectionIntoTokens(section, decodingDictionary)
            for token in tokens:
                decodedToken = ''
                if token != '\n':
                    if token != '~':
                        decodedToken = decodingDictionary[token]
                    else:
                        decodedToken ='~'
                decodedTokenText = decodedTokenText + decodedToken
            decodedSections.append(decodedTokenText)
        print ('||'.join(decodedSections)).encode('utf-8')
