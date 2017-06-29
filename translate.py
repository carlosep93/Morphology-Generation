#!/usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from optparse import OptionParser
import os

usage = "translate.py [--stdin, -f path-to-input-file] [--stdout, -o path-to-output-file]"

parser = OptionParser(usage=usage)
parser.add_option("-i", "--stdin", dest="stdin",
				  help="Standard input", action="store_true")
parser.add_option("-f", "--filein", dest="filein",
				  help="Input file", metavar="filein")
parser.add_option("-s", "--stdout", dest="stdout",
				  help="Standard output", action="store_true")
parser.add_option("-o", "--fileout", dest="fileout",
				  help="Output file", metavar="fileout")


(options, args) = parser.parse_args()

if options.stdin == None and options.filein == None:
	parser.error("Missing input method")
	exit(2)

if options.stdout == None and options.fileout == None:
	parser.error("Missing output method")
	exit(2)


fileIn = ""
fileOut = ""

if options.stdin:
	line =raw_input()
	fileIn = open('temp/input.txt','w')
	print(line,file=fileIn)
	fileIn.close()
	fileIn = 'temp/input.txt'
else:
	fileIn = options.filein

if options.stdout:
	fileOut = 'temp/output.txt'
else:
	fileOut = options.fileout


MOSES_DIR=''
SRILM_DIR=''
BASELINE_DIR=''

config = open('config/config')
for i in config.readlines():
	i = i.replace('\n','')
	if 'MOSES_DIR' in i:
		MOSES_DIR = i.split('=')[1]
	if 'SRILM_DIR' in i:
		SRILM_DIR = i.split('=')[1]	
	if 'BASELINE_DIR' in i:
		BASELINE_DIR = i.split('=')[1]		

config.close()

if MOSES_DIR == '' or SRILM_DIR == '' or BASELINE_DIR == '':
	print("CONFIGURATION ERROR. Please check config file")
	exit(2)

print('Begin Translation')
os.system(MOSES_DIR + '/bin/moses -drop-unknown -mbr  -mp -config ' +\
		BASELINE_DIR + '/test/filtered_test/moses.test.ini ' + \
		'-input-file ' + fileIn + ' > temp/simple-translation')

print('Generating nbest lists')
os.system('rm temp/nbestlist')
os.system('./generateNBest.py -i temp/simple-translation -o temp/nbestlist' )

print('adding language model feature')
os.system('rm temp/nbestsentences')
os.system('./split.py < temp/nbestlist > temp/nbestsentences')
os.system(SRILM_DIR + '/ngram -lm 1-corpus/lm.es -ppl temp/nbestsentences -debug 1 > temp/nbestlm')
os.system('./add_feature.py')

print('rescoring')
os.system('rescore/rescore.py rescore/rescore-work/rescore.ini < temp/nbestfeature > temp/nbestrescored')
os.system('rescore/topbest.py <temp/nbestrescored > temp/final-translation')

print('post processing rules')
os.system('./replace.bash temp/final-translation')
os.system('./conjuntions.py < temp/final-translation > temp/processed-translation')


if (options.stdout):
	translation = open('temp/processed-translation')
	print('\n\n Translation \n\n')
	for line in translation.readlines():
		line = line.replace('\n','')
		print(line)
	print('\n\n')	

else:
	os.system('cp temp/processed-translation ' + options.fileout)		






