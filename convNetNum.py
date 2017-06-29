#-*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import theano
import theano.tensor as T

import re
import numpy as np
import h5py

import utils
import window 
from spanishNumWin import spanishNumWin as swn

from keras.models import Model
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.layers import recurrent
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten, Permute
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM, GRU
from keras.layers import recurrent, Input, merge
from keras.layers.convolutional import Convolution1D, MaxPooling1D, ZeroPadding1D, AveragePooling1D
from keras.optimizers import SGD


MAX_LENGTH = 3
batch_size = 32
nb_filter = 150
filter_length = 1
vocabSize = 9000
nFeatures = vocabSize + 3
embeddingSize = 128 
PATH = '../1-corpus/' 

print("Procesando texto")

training = swn(PATH + 'train/train.removed.es', \
	PATH + 'train/train.zh', PATH + 'train/train.es', \
	PATH + 'train/alignment.zhes',vocabSize,MAX_LENGTH)

dev = swn(PATH + 'dev/dev.removed.es', \
	PATH + 'dev/dev.zh', PATH + 'dev/dev.es', \
	PATH + 'dev/alignment.zhes',vocabSize,MAX_LENGTH)

test = swn(PATH + 'test/test.removed.es', \
	PATH + 'test/test.zh', PATH + 'test/test.es', \
	PATH + 'test/alignment.zhes',vocabSize,MAX_LENGTH)

trainWindows, trainTargets, trainChinese = training.process(True)
devWindows, devTargets, devChinese = dev.process(True)
testWindows, testTargets, testChinese = test.process(True)

vocabulary = utils.getVocabulary(trainWindows,MAX_LENGTH,vocabSize)


trainFeatures = utils.vectorizeWindows(trainWindows,vocabulary)
devFeatures = utils.vectorizeWindows(devWindows,vocabulary)
testFeatures = utils.vectorizeWindows(testWindows,vocabulary)


print("Vocabulario: ", len(vocabulary))

print("Procesado, Creando Modelo")

for 
trainFeatures = sequence.pad_sequences(trainFeatures,maxlen=MAX_LENGTH)
trainTargets = np.asarray(trainTargets)

devFeatures = sequence.pad_sequences(devFeatures,maxlen=MAX_LENGTH)
devTargets = np.asarray(devTargets)

testFeatures = sequence.pad_sequences(testFeatures,maxlen=MAX_LENGTH)
testTargets = np.asarray(testTargets)

model = Sequential()
model.add(Embedding(nFeatures, embeddingSize,input_length=MAX_LENGTH))
model.add(Convolution1D(nb_filter=nb_filter,
						filter_length=filter_length,
						border_mode='valid',
						activation='relu',
						subsample_length=1))
model.add(MaxPooling1D(pool_length=2))
model.add(LSTM(70))
model.add(Dense(70,activation='sigmoid'))
model.add(Dense(3))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy',
			  optimizer='adam', metrics=['accuracy'])


print("Entrenando Modelo")

model.fit(trainFeatures, trainTargets, batch_size=batch_size, nb_epoch=1,
		  validation_data=(devFeatures, devTargets), verbose=1)

score, acc = model.evaluate(testFeatures, testTargets, batch_size=batch_size, verbose=1)

print('Score:', score)
print('Accuracy:', acc)

'''
#guardar modelo y pesos
model_json = model.to_json()
fileModel = open('modeloNumeroSinDet.json','w')
fileModel.write(model_json)
fileModel.close()
model.save_weights('modeloNumeroSinDet.h5')
'''
