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

import utils
import window 
from spanishNumWin import spanishNumWin as swn
from spanishGenWin import spanishGenWin as swg
from conjugate import conjugate

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
from keras.layers.advanced_activations import ThresholdedLinear
from keras.models import model_from_json


vocabSize = 7000
MAX_LENGTH = 7
PATH = '../1-corpus/'
SRILM_PATH = "~/srilm/bin/i686-m64/" 

def read_lines(file):
	while True:
		line = file.readline()
		if not line:
			break
		yield line



def predictedNum(prediction):
	index = prediction.tolist().index(max(prediction))
	if index != 2: 
		num = ['S','0','N','P'] if index == 1 else ['P','0','N','S']
	else:
		num = ['C','S','N','0','S','P']
	return num	

def predictedGen(prediction):
	index = prediction.tolist().index(max(prediction))
	if index != 2:
		gen = ['M','F','C','S','N','0'] if index == 1 else ['F','M','C','S','N','0']
	else:
		if prediction.tolist()[0] > prediction.tolist()[1]:
			gen = ['C','S','N','0','M','F']	
		else:
			gen = ['C','S','N','0','F','M']
	return gen


def predictedIndex(prediction):
	return prediction.tolist().index(max(prediction))
	 	

def getLmProbability(group):
	srilmText = open('srilm/bigram.txt', 'w')
	srilm.write(group)
	srilmText.close()
	os.system(SRILM_PATH + 'ngram-count -text srilm/bigram.txt -order 2 -write srilm/bigram.count -addsmooth 0 -lm srilm/bigram.lm')
	os.system(SRILM_PATH + 'make-ngram-pfsg srilm/bigram.lm > srilm/bigram.pfsg')
	os.system(SRILM_PATH + './lattice-tool -vocab ~/Documentos/TFG/repo/tfg/freeling/vocabulary.txt -nbest-decode 1 -in-lattice srilm/bigram.pfsg -out-nbest-dir srilm')
	os.system('gunzip BIGRAM_PFSG')
	scoreFile = open('srilm/BIGRAM_PFSG', 'r')
	score = 10 ** scoreFile.read().split(' ')[0]
	scoreFile.close()
	return score

def rescoringGenNum(gen, num, line, word):
	group = line[-1] + " " if len(line) != 0 else '<s> '
	numTag = 'S' if round(num) == 1 else 'P'
	genTag = 'M' if round(gen) == 1 else 'F'
	tagggedWords = generateTag(word,[numTag],[genTag,'0'])
	next = [i for i in conj.conjugateWords(taggedWords) if '[' not in i]
	if len(next) != 0:
		group += next[0]
		lmProb = getLmProbability(group)


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
			else:
				tags.append(tagOthers(tag,lemma,g,n))
	return tags					




print("Cargando modelos")

fileModelGen = open('modeloGenero.json')
model_json = fileModelGen.read()
fileModelGen.close()

modeloGenero = model_from_json(model_json)
modeloGenero.load_weights('modeloGenero.h5')


fileModelNum = open('modeloNumero.json')
model_json = fileModelNum.read()
fileModelNum.close()

modeloNumero = model_from_json(model_json)
modeloNumero.load_weights('modeloNumero.h5')

modeloNumero.compile(loss='binary_crossentropy',
              optimizer='adam',
              class_mode="binary")

modeloGenero.compile(loss='binary_crossentropy',
              optimizer='adam',
              class_mode="binary")


print("Cargando diccionarios")

conj = conjugate("../freeling/dicc.src", "../freeling/afixos.dat", "../freeling/conjugations")

print("Cargando texto")

trainingNum = swn(PATH + 'train/train.gennum.es', \
	PATH + 'train/train.zh', PATH + 'train/train.es', \
	PATH + 'train/alignment.zhes',vocabSize,MAX_LENGTH)

textNum = swn(PATH + 'test/test.gennum.es', \
	PATH + 'test/test.zh', PATH + 'test/test.es', \
	PATH + 'test/alignment.zhes',vocabSize,MAX_LENGTH)

trainingGen = swg(PATH + 'train/train.gennum.es', \
	PATH + 'train/train.zh', PATH + 'train/train.es', \
	PATH + 'train/alignment.zhes',vocabSize,MAX_LENGTH)

textGen = swg(PATH + 'test/test.gennum.es', \
	PATH + 'test/test.zh', PATH + 'test/test.es', \
	PATH + 'test/alignment.zhes',vocabSize,MAX_LENGTH)


numWindows, numTargets, numTags = textNum.process(True)
genWindows, genTargets, genTags = textGen.process(True)

trainNum, targetsNum, a = trainingNum.process(True)
trainGen, targetsGen, a = trainingGen.process(True)

numVocabulary = utils.getVocabulary(trainNum)
genVocabulary = utils.getVocabulary(trainGen)

numFeatures = sequence.pad_sequences(utils.vectorizeWindows(numWindows,numVocabulary),maxlen=MAX_LENGTH)
genFeatures = sequence.pad_sequences(utils.vectorizeWindows(genWindows,genVocabulary),maxlen=MAX_LENGTH)

mid = MAX_LENGTH/2

numWords = [w[mid] for w in numWindows]
genWords = [w[mid] for w in genWindows]

words = [w.replace('\n','') for w in numWords]


predsGen = modeloGenero.predict(genFeatures)
predsNum = modeloNumero.predict(numFeatures)


def getNum(correctWord):
	if correctWord[0] == 'V':
		return correctWord[5]
	elif correctWord[0] == 'N':
		return 	correctWord[2]
	else:
		return correctWord[4]	

def getGen(correctWord):
	if correctWord[0] == 'V':
		return correctWord[6]
	elif correctWord[0] == 'N':
		return 	correctWord[2]
	else:
		return correctWord[3]	



print("Generando texto")

fileText = open(PATH + 'test/test.gennum.es')
fileOut = open('genText.txt','a+w')
miss = 0
affix = ''
add = False
count = 0
for line in read_lines(fileText):
	genline = ""
	line = line.replace('\n','')
	for w in line.split(' '):
		count += 1
		
		if '[' not in w:
			genline += w + " "

		else:
			if words[0] == w:

				num = predictedNum(predsNum[0])
				gen = predictedGen(predsGen[0])
				
				if '+' in w:
					add = True
					affix = w[w.index('+')+1:w.index(']')]
					w = w[:w.index('+')] + ']'
				
				taggedWords= generateTag(w,num,gen)
				next = [i for i in conj.conjugateWords(taggedWords) if '[' not in i and len(i) != 0]
				if len(next) != 0: 
					genline += next[0] + " "
				else:
					lemma = w[w.index('[')+1:-1]
					genline +=  lemma + " "
					#print(w, taggedWords)	
					miss += 1
					
				if add:
					add = False
					genline = genline[:-1] + affix	+ " "
				
				words.pop(0)
				predsNum = np.delete(predsNum,(0),axis=0)
				predsGen = np.delete(predsGen,(0),axis=0)
				
	genline = genline[:-1] 					
	print(genline,file=fileOut)	


print("missed: " + str(miss))
print("total: " , count)		
fileOut.close()
fileText.close()