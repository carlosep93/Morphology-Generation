#!/usr/bin/python
# -*- coding: utf-8 -*-

class mdict(dict):

    def __setitem__(self, key, value):
        """add the given value to the list of values for this key"""
        self.setdefault(key, []).append(value)

from optparse import OptionParser
import re
import sys

usage = "usage: %prog -d freeling-dicc.src -c path-to-conjugation-rules -a prefixes-sufixes-file"
parser = OptionParser(usage=usage)
parser.add_option("-d", "--dictionary", dest="dictionary",
                  help="Freeling Inflected Forms Dictionary", metavar="dictionary")
parser.add_option("-a", "--affixes", dest="affixes",
                  help="Path to Affixes Dictionary", metavar="affixes")
parser.add_option("-c", "--conjrules", dest="conjrules",
                  help="Path to Conjugation Rules Dictionary", metavar="conjrules")


(options, args) = parser.parse_args()

if options.dictionary == None:
    parser.error("Freeling Inflected Forms Dictionary not specified")
    exit(2)
if options.conjrules == None:
    parser.error("Path to Conjugation Rules Dictionary not specified")
    exit(2)
if options.affixes == None:
    parser.error("Path to Affixes dictionary")
    exit(2)


dh=open(options.dictionary,'r')
ah=open(options.affixes,'r')

c1h=open(options.conjrules+'/1conj.rules','r')
c2h=open(options.conjrules+'/2conj.rules','r')
c3h=open(options.conjrules+'/3conj.rules','r')
dicc=mdict()

c1=mdict()
c2=mdict()
c3=mdict()

prefixes={}
suffixes={}

sys.stderr.write('Loading Freeling Dictionary...\n')
for dl in dh:
    #Obtain words and alignments
    dl=dl.strip().split(' ')
    value=dl[0];
    i=1;
    while i<len(dl)-1:
        key=dl[i]+'|'+dl[i+1]
        dicc[key]=value
        i+=2

dh.close()    

isPrefix=0
isSuffix=0
sys.stderr.write('Loading Freeling Affixes...\n')
for al in ah:
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
                    prefixes[al[0]]=al[2:]
                else:
                    #print 'Suffix',
                    #print al
                    suffixes[al[0]]=al[2:]
        
ah.close()
sys.stderr.write('Loading 1st conjugation...\n')
for c1l in c1h:
    c1l=c1l.strip().split(' ')
    c1[c1l[0]]=c1l[1]
c1h.close()

sys.stderr.write('Loading 2nd conjugation...\n')
for c2l in c2h:
    c2l=c2l.strip().split(' ')
    c2[c2l[0]]=c2l[1]
c2h.close()

sys.stderr.write('Loading 3rd conjugation...\n')
for c3l in c3h:
    c3l=c3l.strip().split(' ')
    c3[c3l[0]]=c3l[1]    
c3h.close()


for sl in sys.stdin:
    sl=sl.strip().split(' ')
    for w in range(len(sl)):
        m=re.match(r'(\S*)\[(\S*)\]',sl[w])
        if m:
            m=m.groups()
            if (dicc.has_key(m[1]+'|'+m[0])):
                for i in range(0,len(dicc[m[1]+'|'+m[0]])): 
                    sl[w]=dicc[m[1]+'|'+m[0]][i]
            else:
                #Mirar si ha tingut algun prefix o suffix
                succ=0
                for pref in prefixes:
                    if (m[1][0:len(pref)]==pref and dicc.has_key(m[1][len(pref):]+'|'+m[0])):
                        for i in range(0,len(dicc[m[1][len(pref):]+'|'+m[0]])): 
                            sl[w]=pref+dicc[m[1][len(pref):]+'|'+m[0]][i]
                        succ=1
                        break
                    
                try:    
                    if succ==0:
                        #Mirar si el lema acaba en ar er o ir
                        if (m[1][-2:]=='ar' or m[1][-2:]=='ár'):
                            for i in range(0,len(c1[m[0]])):
                                sl[w]=m[1][0:-2]+c1[m[0]][i]
                        elif (m[1][-2:]=='er' or m[1][-2:]=='ér'):
                            for i in range(0,len(c2[m[0]])):
                                sl[w]=m[1][0:-2]+c2[m[0]][i]
                        elif (m[1][-2:]=='ir' or m[1][-2:]=='ír'):
                            for i in range(0,len(c3[m[0]])):
                                sl[w]=m[1][0:-2]+c3[m[0]][i]
                        else:
                            print m[1],
                except KeyError:
                    pass                                
    print " ".join(sl)
