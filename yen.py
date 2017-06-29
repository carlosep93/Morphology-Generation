#-*- coding: utf-8 -*-

from node import Node
from node import Graph

def getKBestPaths(graph, k):
	A = []
	B = []
	length = graph.getLength() -1
	A.append(graph.getBestPath(0,length))
	
	for k in range(1,k):

		for i in range(0,length):
			spurNode = A[k-1][i]
			rootPath = A[k-1][:i]
			linksRemoved = []
			nodesRemoved = []
			
			for path in A:
				if rootPath == path[:i] and i != length:
					linksRemoved.append((i,path[i],path[i+1]))
					graph.changeStateLink(i,path[i],path[i+1], False)

			for j,node in enumerate(rootPath):
				if j != i and node != spurNode:
					graph.changeStateNode(j,node,False)
					nodesRemoved.append((j,node))

			spurPath = graph.getBestPath(i, length, spurNode)		
			totalPath = rootPath + spurPath

			if len(totalPath) == length+1:
				weight = graph.getPathCost(totalPath)
				if (totalPath,weight) not in B:
					B.append((totalPath,weight))

			for tuple in linksRemoved:
				layer, node, next = tuple
				graph.changeStateLink(layer,node,next,True)

			for pair in nodesRemoved:
				layer, node = pair
				graph.changeStateNode(layer,node,True)	

		if len(B) == 0:
			break


		B.sort(key= lambda x: x[1], reverse=True)
		A.append(B[0][0])
		B.pop(0)

	return A	



'''
sentence = Graph()
word1 = [Node('La',0.8),Node('El',0.03),Node('Los',0.12),Node('Los',0.05)]
word2 = [Node('casa', 0.99), Node('casas',0.01)]
word3 = [Node('roja', 0.72), Node('rojo', 0.05), Node('rojas', 0.10), Node('rojas', 0.13)]
word4 = [Node('del',1)]
word5 = [Node('bosques',0.25),Node('bosque',0.75)]

sentence.setLayer(word1)
sentence.setLayer(word2)
sentence.setLayer(word3)
sentence.setLayer(word4)
sentence.setLayer(word5)

#sentence.changeStateLink(3,0,1,False)
#sentence.changeStateLink(0,0,0,False)

#print sentence.printGraph()


#sentence.changeStateNode(3,0,False)
#print sentence.getNode(3,0).getLinks()
print sentence.getBestPath(0,4)



#print sentence.getBestPath(0,4)

paths = []
k = 20
while len(paths) != k:
	paths = getKBestPaths(sentence,k)
	if len(paths) == k:
		break
	ini = paths[0][0]
	sentence.changeStateNode(0,ini,False)


paths =  getKBestPaths(sentence,100)

for i in paths:
	print sentence.getSentence(i)
'''		
