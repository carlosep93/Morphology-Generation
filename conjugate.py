# -*- coding: utf-8 -*-

from optparse import OptionParser
import re
import sys

class mdict(dict):

	def __setitem__(self, key, value):
		"""add the given value to the list of values for this key"""
		self.setdefault(key, []).append(value)


class conjugate():

	def __init__(self, dicPath, afixPath, conjDir):
		dicFile=open(dicPath,'r')
		afixFile=open(afixPath,'r')
		c1h=open(conjDir+'/1conj.rules','r')
		c2h=open(conjDir+'/2conj.rules','r')
		c3h=open(conjDir+'/3conj.rules','r')
		self.c1=mdict()
		self.c2=mdict()
		self.c3=mdict()
		self.dict=mdict()
		self.prefixes={}
		self.suffixes={}

		for line in dicFile:
		#Obtain words and alignments
			line=line.strip().split(' ')
			value=line[0];
			i=1;
			while i<len(line)-1:
				key=line[i]+'|'+line[i+1]
				self.dict[key]=value
				i+=2

		dicFile.close()

		isPrefix=0
		isSuffix=0
		#Loading Freeling Affixes...
		for al in afixFile:
			#Obtain words and alignments
			al=al.rstrip()
			al=al.lstrip()
			if (len(al) and al[0]!='#'):
				if (al=='<Prefixes>'):
					isSuffix=0
					isPrefix=1
				elif (al=='</Prefixes>'):
					isPrefix=0
				elif (al=='<Suffixes>'):
					isSuffix=1
					isPrefix=0
				elif (al=='</Suffixes>'):
					isSuffix=0
				elif (isPrefix==1 or isSuffix==1):
					al=al.strip().split('\t')
					match1=re.search(r'V',al[2])
					match2=re.search(r'[V\*]',al[3])
					if match1 and match2:
						if isPrefix:
							#print 'Prefix',
							#print al
							self.prefixes[al[0]]=al[2:]
						else:
							#print 'Suffix',
							#print al
							self.suffixes[al[0]]=al[2:]
				
		afixFile.close()

		sys.stderr.write('Loading 1st conjugation...\n')
		for c1l in c1h:
			c1l=c1l.strip().split(' ')
			self.c1[c1l[0]]=c1l[1]
		c1h.close()

		sys.stderr.write('Loading 2nd conjugation...\n')
		for c2l in c2h:
			c2l=c2l.strip().split(' ')
			self.c2[c2l[0]]=c2l[1]
		c2h.close()

		sys.stderr.write('Loading 3rd conjugation...\n')
		for c3l in c3h:
			c3l=c3l.strip().split(' ')
			self.c3[c3l[0]]=c3l[1]    
		c3h.close()



	def conjugateWords(self,words):
		result = []
		for sl in words:
			sl=sl.strip().split(' ')
			for w in range(len(sl)):
				m=re.match(r'(\S*)\[(\S*)\]',sl[w])
				if m:
					m=m.groups()
					if (self.dict.has_key(m[1]+'|'+m[0])):
						for i in range(0,len(self.dict[m[1]+'|'+m[0]])): 
							sl[w]=self.dict[m[1]+'|'+m[0]][i]
					else:
						#Mirar si ha tingut algun prefix o suffix
						succ=0
						for pref in self.prefixes:
							if (m[1][0:len(pref)]==pref and self.dict.has_key(m[1][len(pref):]+'|'+m[0])):
								for i in range(0,len(self.dict[m[1][len(pref):]+'|'+m[0]])): 
									sl[w]=pref+self.dict[m[1][len(pref):]+'|'+m[0]][i]
								succ=1
								break
										
						if succ==0:
							#Mirar si el lema acaba en ar er o ir
							try:
								if (m[1][-2:]=='ar' or m[1][-2:]=='ár'):
									for i in range(0,len(self.c1[m[0]])):
										sl[w]=m[1][0:-2]+self.c1[m[0]][i]
								elif (m[1][-2:]=='er' or m[1][-2:]=='ér'):
									for i in range(0,len(self.c2[m[0]])):
										sl[w]=m[1][0:-2]+self.c2[m[0]][i]
								elif (m[1][-2:]=='ir' or m[1][-2:]=='ír'):
									for i in range(0,len(self.c3[m[0]])):
										sl[w]=m[1][0:-2]+self.c3[m[0]][i]	
							except KeyError:
								pass				
			result.append(" ".join(sl))
		return result