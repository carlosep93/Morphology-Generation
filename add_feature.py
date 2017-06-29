#!/usr/bin/python
#-*- coding: utf-8 -*
from __future__ import absolute_import
from __future__ import print_function

import sys
import math

def read_lines(file):
	while True:
		line = file.readline()
		if not line:
			break
		yield line

lm = open('temp/nbestlm','r')
weights = open('temp/nbestlist','r')
out = open('temp/nbestfeature','w+a')

for line in read_lines(weights):
	line = line.replace('\n','')
	num, sentence, score = line.split(' ||| ')
	score1, score2 = score.split()
	
	linelm = next(read_lines(lm))
	linelm = next(read_lines(lm))
	linelm = next(read_lines(lm))
	linelm = linelm.split()
	lmFeat = 'Feature0= ' + linelm[3]
	modelFeat = 'Feature1= ' + str(math.log10(float(score1)))  #+ " " + str(math.log10(float(score2)))
	print(' ||| '.join([num, sentence, lmFeat + ' ' + modelFeat, "-1"]),file=out)
	
	linelm = next(read_lines(lm))

lm.close()
weights.close()
out.close()
