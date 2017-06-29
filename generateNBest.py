#!/usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import theano
import theano.tensor as T
import sys

import re
import numpy as np
import h5py
import os
from sys import argv
from optparse import OptionParser

import utils
import window 
from spanishNumWin import spanishNumWin as swn
from spanishGenWin import spanishGenWin as swg
from conjugate import conjugate
from node import Node as node
from node import Graph as Graph
import yen as yen

from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.layers import recurrent
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM
from keras.layers import recurrent
from keras.layers.convolutional import Convolution1D, MaxPooling1D
from keras.optimizers import SGD
from keras.models import model_from_json


numberDict = {'S':['S','P','C','N','0'],'P':['P','S','C','N','0'],'N':['C','N','0','P','S']}
genderDict = {'M':['M','F','C','N','0'],'F':['F','M','C','N','0'],'N':['C','N','0','F','M']}
vocabSize = 7000
MAX_LENGTH = 7
PATH = '1-corpus/'
SRILM_PATH = "~/srilm/bin/i686-m64/" 
K = 100

def read_lines(file):
	while True:
		line = file.readline()
		if not line:
			break
		yield line


def predictedNum(pred):
	index = pred.tolist().index(max(pred))
	if index != 2: 
		num = [('S',pred[1]),('P',pred[0]),('C',pred[2]),('N',pred[2]),('0',pred[2])] \
			if index == 1 else [('P',pred[0]),('S',pred[1]),('C',pred[2]),('N',pred[2]),('0',pred[2])]
	else:
		if pred.tolist()[0] > pred.tolist()[1]:
			num = [('C',pred[2]),('N',pred[2]),('0',pred[2]),('P',pred[0]),('S',pred[1])]
		else:
			num = [('C',pred[2]),('N',pred[2]),('0',pred[2]),('S',pred[1]),('P',pred[0])]	
	return num	

def predictedGen(pred):
	index = pred.tolist().index(max(pred))
	if index != 2:
		gen = [('M',pred[1]),('F',pred[0]),('C',pred[2]),('N',pred[2]),('0',pred[2])] \
			if index == 1 else [('F',pred[1]),('M',pred[0]),('C',pred[2]),('N',pred[2]),('0',pred[2])]
	else:
		if pred.tolist()[0] > pred.tolist()[1]:
			gen = [('C',pred[2]),('N',pred[2]),('0',pred[2]),('M',pred[1]),('F',pred[0])]	
		else:
			gen = [('C',pred[2]),('N',pred[2]),('0',pred[2]),('F',pred[0]),('M',pred[1])]
	return gen			



def predictedIndex(prediction):
	return prediction.tolist().index(max(prediction))

def tagVerb(tag,lemma,gen,num):
	return tag + num + gen + '[' + lemma + ']'

def tagNoun(tag, lemma, gen, num):
	return tag[:2] + gen + num + tag[2:] + '[' + lemma + ']'	

def tagOthers(tag, lemma, gen, num):	
	return tag[:3] + gen + num + tag[3:] + '[' + lemma + ']'


def generateTag(word,nums,gens):
	sep = word.index('[')
	tag = word[:sep]
	lemma = word[sep+1:-1]
	tags = []
	#print(tag,lemma)
	for n in nums:
		for g in gens:
			if word[0] == 'V':
				tags.append(tagVerb(tag,lemma,g,n))
			elif word[0] == 'N':
				tags.append(tagNoun(tag,lemma,g,n))
			elif word[0] in ['Z','S']:
				tags.append(word)
			else:
				tags.append(tagOthers(tag,lemma,g,n))
	return tags
					
def conjugateAffix(affix, gen, num):
	
	affixDict = {'se':'P00000', 'le':'PP3D00', 'te': 'PP2000', 'lo': 'PP3A00', 'me': 'PP1000'}
	conjugatedWord = affix
	
	if affixDict.has_key(affix):
		tag = affixDict[affix]
		word = tag + '[' + affix + ']'
		taggedWords  = generateTag(word,gen,num)
		forms = [ i for i in conj.conjugateWords(taggedWords) if '[' not in i]
		if len(forms) != 0:
			conjugatedWord =  forms[0]
		
	return conjugatedWord


def addPronoun(verb, affix, gen, num):
	dict = {'a':'á','e':'é','i':'í','o':'ó', 'u':'ú'}
	found = False
	for i in dict.values():	
		if i in verb:
			found = True
	if not verb[-1] in dict.keys():
		found = True
	if not found:
		second = False
		verb[-1] in []	
		for i in range(len(verb)-1,0,-1):
			if verb[i] in dict.keys():
				if second:
					verb = verb[:i] + dict[verb[i]] + verb[i+1:]
					break
				else:
					second = True
	
	affix = conjugateAffix(affix,gen,num)
	return verb + affix
	
def makeArrayWeights(num,gen):
	arrayNum = ['P','S','N']
	arrayGen = ['F','M','N']	
	for i in range(3):
		arrayNum[i] = (arrayNum[i],num[i])
		arrayGen[i] = (arrayGen[i],gen[i])
	return arrayNum, arrayGen	

usage='generateText.py -i input-file -o output-file'
parser = OptionParser(usage=usage)
parser.add_option("-i", "--input", dest="input",
				  help="Input text", metavar="input")
parser.add_option("-o", "--output", dest="output",
				  help="Output file", metavar="output")

(options, args) = parser.parse_args()

if options.input == None:
	parser.error("Missing input text file")
	exit(2)
if options.output == None:
	parser.error("Missing output file")
	exit(2)	


print("Loading models")

fileModelGen = open('models/modeloGenero.json')
model_json = fileModelGen.read()
fileModelGen.close()

modeloGenero = model_from_json(model_json)
modeloGenero.load_weights('models/modeloGenero.h5')


fileModelNum = open('models/modeloNumero.json')
model_json = fileModelNum.read()
fileModelNum.close()

modeloNumero = model_from_json(model_json)
modeloNumero.load_weights('models/modeloNumero.h5')

modeloNumero.compile(loss='binary_crossentropy',
              optimizer='adam',
              class_mode="binary")

modeloGenero.compile(loss='binary_crossentropy',
              optimizer='adam',
              class_mode="binary")


print("Loading freeling dictionaries")

conj = conjugate("freeling/dicc.src", "freeling/afixos.dat", "freeling/conjugations")



print("Loading vocabulary")

trainingNum = swn(PATH + 'train/train.removed.es', \
	PATH + 'train/train.zh', PATH + 'train/train.es', \
	PATH + 'train/alignment.zhes',9000,9)

textNum = swn(options.input, \
	options.input, options.input, \
	options.input,9000,9)

trainingGen = swg(PATH + 'train/train.removed.es', \
	PATH + 'train/train.zh', PATH + 'train/train.es', \
	PATH + 'train/alignment.zhes',7000,7)

textGen = swg(options.input, \
	options.input, options.input, \
	options.input,7000,7)


numWindows, numTargets = textNum.process(False)
genWindows, genTargets = textGen.process(False)

trainNum, targetsNum = trainingNum.process(True)
trainGen, targetsGen = trainingGen.process(True)

numVocabulary = utils.getVocabulary(trainNum,7,9000)
genVocabulary = utils.getVocabulary(trainGen,7,7000)

numFeatures = sequence.pad_sequences(utils.vectorizeWindows(numWindows,numVocabulary),maxlen=9)
genFeatures = sequence.pad_sequences(utils.vectorizeWindows(genWindows,genVocabulary),maxlen=7)

mid = MAX_LENGTH/2

numWords = [w[mid] for w in numWindows]
genWords = [w[mid] for w in genWindows]

words = [w.replace('\n','') for w in genWords]


predsGen = modeloGenero.predict(genFeatures)
predsNum = modeloNumero.predict(numFeatures)


def getNum(correctWord):
	if correctWord[0] == 'V':
		return correctWord[5]
	elif correctWord[0] == 'N':
		return 	correctWord[3]
	else:
		return correctWord[4]	

def getGen(correctWord):
	if correctWord[0] == 'V':
		return correctWord[6]
	elif correctWord[0] == 'N':
		return 	correctWord[2]
	else:
		return correctWord[3]	



fileText = open(options.input)
fileOut = open(options.output,'a+w')

miss = 0
affix = ''
add = False
count = 0

for line in read_lines(fileText):

	graphNum = Graph()
	graphGen = Graph()

	line = line.replace('\n','')
	for w in line.split( ):
		if '[' not in w:
			graphNum.setLayer(['N'],[1])
			graphGen.setLayer(['N'],[1]) 

		else:
			if len(words) != 0 and words[0] == w:
				graphNum.setLayer(['P','S','N'],list(predsNum[0]))
				graphGen.setLayer(['F','M','N'], list(predsGen[0]))
				words.pop(0)
				predsNum = np.delete(predsNum,(0),axis=0)
				predsGen = np.delete(predsGen,(0),axis=0)
			
			else:
				graphNum.setLayer(['N'],[1])
				graphGen.setLayer(['N'],[1])

	pathsNum = yen.getKBestPaths(graphNum,K)
	pathsGen = yen.getKBestPaths(graphGen,1)
		
	for i in range(len(pathsNum)):
		sentenceNum, weightNum = graphNum.getSentence(pathsNum[i])
		sentenceGen, weightGen = graphGen.getSentence(pathsGen[0])	
		genline = []
		for l,act in  enumerate(line.split()):
			
			if '[' not in act:
				genline.append(act)
			
			elif act[0] in ['A','V','N','D','P','S']:
	
				num = numberDict[sentenceNum.split()[l]]
				gen = genderDict[sentenceGen.split()[l]]
				
				if '+' in act and act[0] == 'V' :				
					add = True
					affix = act[act.index('+')+1:act.index(']')]
					act = act[:act.index('+')] + ']'

				taggedWords = generateTag(act,num,gen)
				next = [j for j in conj.conjugateWords(taggedWords) if '[' not in j and len(j) != 0]
				if len(next) != 0: 
					genline.append(addPronoun(next[0],affix,gen,num)  if add else next[0]) 
				else:
					lemma = act[act.index('[')+1:-1]
					genline.append(lemma)	 
			else:
				lemma = act[act.index('[')+1:-1] if'[' in  act  else act
				genline.append(lemma)
			
			affix=''
			add = False
			
			if genline[-1] == 'de+el':
				genline[-1] = 'del'
			if genline[-1] == 'a+el':
				genline[-1] = 'al'
	 
		print(str(count) + ' ||| ' + str(' '.join(genline))  + ' ||| ' +  str(weightNum) + ' ' + str(weightGen) , file=fileOut)

	count += 1
									
fileOut.close()
fileText.close()
