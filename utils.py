#-*- coding: utf-8 -*-
import numpy as np
import operator

def vectorizeWindows(windows,vocabulary):
	vectorizedWindows = []
	for i, group in enumerate(windows):
		indexes = []
		for g in group:
			if g not in ( '<s>', '<e>'):
				try:
					indexes.append(vocabulary.index(g)+1)
				except ValueError:
					#Token desconocido
					indexes.append(len(vocabulary)+1)	
			else:
				if g == '<s>':
					indexes.append(0)
				else:
					indexes.append(len(vocabulary)+2)	
		vectorizedWindows.append(indexes)		 
	return vectorizedWindows


def vectorizeSentences(features,corpus):
	vectorizedSentences = []
	for i, group in enumerate(features):
		indexes = []
		for g in group:
			if g != u'':
				indexes.append(corpus.index(g)+1)
		vectorizedSentences.append(indexes)		 
	return vectorizedSentences


def makeClasses(targets):
	classes = np.empty((0,2), dtype=theano.config.floatX)	
	for i in targets:
		act = np.array([1.0,0.0]) if i == 0 else np.array([0.0,1.0])
		classes = np.vstack([classes,act])
	return classes	

			
def softmax(x):
	return T.nnet.softmax(x)

def myRelu(x):
	return max(0,x)				

def getVocabulary(windows,winSize=7,vocabSize=7000):
	vocabulary = {}
#	mid = winSize/2 if winSize % 2 == 0 else winSize/2 + 1
	for w in windows:
		for l in w:
			if vocabulary.has_key(l):
				vocabulary[l] += 1
			else:
				vocabulary[l] = 1

	pairs = vocabulary.items()
	pairs = sorted(pairs, key=lambda x: x[1], reverse=True) 
	orderedVocabulary = [x[0] for x in pairs]
	orderedVocabulary = orderedVocabulary[:vocabSize]  \
	if vocabSize < len(orderedVocabulary) and vocabSize != 0 \
	else orderedVocabulary					

	return orderedVocabulary



def getNgramVocabulary(windows, n=2, vocabSize=7000):  	
	ngrams = {}
	for w in windows:
		for i in range(len(w)-n):
			act = '-'.join(w[i:i+n])
			if ngrams.has_key(act):
				ngrams[act] += 1
			else:
				ngrams[act] = 1
	ngrams_sorted = sorted(ngrams.iteritems(),  \
					key=operator.itemgetter(1), \
					reverse=True)[0:vocabSize]
	return [x[0] for x in ngrams_sorted]

def vectorizeNgram(windows,vocabulary,start,n=2):
	vectors = []
	for w in windows:
		indexes = []
		for i in range(len(w)-n):
			act = '-'.join(w[i:i+n])
			try:
				indexes.append(vocabulary.index(act) + start)
			except ValueError:
				indexes.append(len(vocabulary))
		vectors.append(indexes)
	return vectors			
	

			

	
