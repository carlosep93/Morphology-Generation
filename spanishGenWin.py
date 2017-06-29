#-*- coding: utf-8 -*-
from window import window

class spanishGenWin(window):

	def __init__(self,textEs,textZh,textTg, align, vocabSize=7000, winSize = 7):
		super(spanishGenWin,self).__init__(textEs,textZh,textTg, align, vocabSize, winSize)
		self.dictPos = {'V':6, 'N':2,'A':3,'S':3,'D':3, 'P':3}
		self.dictTg = {'M':1, 'F':0}

	
	def getTarget(self, word):
		word, base, POS = word.split('|')
		target = [0.0,0.0,0.0]
		if self.dictPos.has_key(POS[0]):
			try:
				index = self.dictPos[POS[0]]
				index = self.dictTg[POS[index]]
				target[index] = 1.0
			except KeyError:
				target[2] = 1.0
		else:
			target[0] = -1
		return target				
	
