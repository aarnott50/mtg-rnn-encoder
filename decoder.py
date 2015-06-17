#!/usr/bin/python
#coding: utf8

from sys import argv
import sys
import json
import codecs


script, decodingDictionaryFileName, decodingTargetFileName = argv

# Currently a bit buggy. Some single character keys aren't getting decoded properly.
def breakSectionIntoTokens(section, decodingDictionary):
    tokens = []
    currentToken = ''
    currentIndexStart = 0
 
    token = ''
    currentIndexEnd = 1
    while len(section) > 0:
        token = token + section[0]
        section = section[1:]
#        print 'token --> ' + token
        if token not in decodingDictionary and token != '\n':
#        if token not in decodingDictionary:
            tokens.append(''.join(token[:-1]))
            token = token[-1]

    tokens.append(token)    

    return tokens

decodingDictionary = None
with codecs.open(decodingDictionaryFileName, encoding='utf-8') as fileHandle:
    fileContents = fileHandle.read()
    decodingDictionary = json.loads(fileContents)

with codecs.open(decodingTargetFileName, encoding='utf-8') as fileHandle:
    lines = fileHandle.readlines()
    for line in lines:
        splitLine = line.split('_')

        print splitLine
        decodedSections = []
        for section in splitLine:
            decodedTokenText = ''
            tokens = breakSectionIntoTokens(section, decodingDictionary)
#            print [section]
#            print tokens
            for token in tokens:
                if token != '\n':
                    if token != '~':
                        decodedTokenText = decodedTokenText + decodingDictionary[token]
                    else:
                        decodedTokenText = decodedTokenText + '~'
            decodedSections.append(decodedTokenText)
        print '*****'
        print ('||'.join(decodedSections)).encode('utf-8')
