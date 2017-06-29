#!/usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import sys

def read_lines(file):
	while True:
		line = file.readline()
		if not line:
			break
		yield line


for line in sys.stdin:
	line = line.replace('\n','')
	line = line.split()
	for i in range(len(line)):
		if line[i] in ['y','o'] and i+1 < len(line):
			if line[i] == 'y' and (line[i+1][0] == 'i' or line[i+1][:2] == 'hi'):
				line[i] = 'e'
			if line[i] == 'o' and (line[i+1][0] == 'o' or line[i+1][:2] == 'ho'):
				line[i] = 'u'
	print(' '.join(line))


