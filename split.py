#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys

def removeGenNum(tag):
	result = ''
	if tag[0] in ['N']:
		result = tag[:2] + tag[4:]
	elif tag[0] == 'V':
		result = tag[:5]
	elif tag[0] in ['P','D','A']:
		result = tag[:3] + tag[5:]
	else:	
		result = tag
	return result
		 


for line in sys.stdin:
	line = line.replace('\n','')
	num,sentence,score = line.split(' ||| ')
	#newline += tag + '[' + lemma + ']' + ' '
	#newline.append(conj + '|' + lemma + '|' +  removeGenNum(tag)) 
	print(sentence)
	

