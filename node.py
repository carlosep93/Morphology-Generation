#-*- coding: utf-8 -*-

class Node(object):

	def __init__(self,word,weight):
		self.word = word
		self.weight = weight
		self.active = True
		self.links = []

	def getWord(self):
		return self.word
	
	def getWeight(self):
		return self.weight

	def changeState(self,newState):
		self.active = newState

	def changeLink(self, index, newState):
		self.links[index] = newState		

	def isActive(self):
		return self.active

	def setLinks(self, size):
		self.links = [True]*size

	def getLinks(self):
		return self.links

	def printNode(self):
		print "word: ", self.word
		print "weight: ", self.weight
		print "active: ", self.active
		print "links: ", self.links	


class Graph(object):
	
	def __init__(self):
		self.Layers = []

	def setLayer(self,arrayWords,arrayWeights):
		arrayNodes = []
		for i in range(len(arrayWords)):
			arrayNodes.append(Node(arrayWords[i], arrayWeights[i]))
		self.Layers.append(arrayNodes)
		self.setLinksLayer(len(arrayNodes))

	def setLinksLayer(self,size):
		i = len(self.Layers)-2
		if i >= 0:
			for node in self.Layers[i]:
				node.setLinks(size)			

	def getNode(self,layer,position):
		return self.Layers[layer][position]

	def getBestPath(self,iniLayer, endLayer, spurNode=-1):
		path = []

		index = -1	
		if spurNode == -1:
			max  = 0.0
			for i,node in enumerate(self.Layers[iniLayer]):
				if max < node.getWeight():					
					index = i
					max = self.Layers[iniLayer][i].getWeight()
		else:
			index = spurNode				

		path.append(index)				
		iniLayer += 1

		while endLayer >= iniLayer:
			index = -1
			max = 0.0

			for i,node in enumerate(self.Layers[iniLayer]):
				if max < node.getWeight() \
					and node.isActive() \
					and self.Layers[iniLayer-1][path[-1]].getLinks()[i]:
					index = i
					max = self.Layers[iniLayer][i].getWeight()

			if index != -1: 
				path.append(index)
			else:
				return []
			iniLayer += 1
		return path

	def getPathCost(self,nodeArray):
		cost = 1.0
		for i,node in enumerate(nodeArray):
			cost *= self.Layers[i][node].getWeight()
		return cost	


	def getLength(self):
		return len(self.Layers)

	def changeStateNode(self,layer,index,newState):
		return self.Layers[layer][index].changeState(newState)

	def changeStateLink(self, layer, index, next, newState):
		self.Layers[layer][index].changeLink(next,newState)

	def isNodeActive(self,layer,index):
		return self.Layers[layer][index].isActive()

	def getSentence(self,array):
		words = []
		totalWeight = 1	
		for i,l in enumerate(self.Layers):
			words.append(l[array[i]].getWord())
			totalWeight *= l[array[i]].getWeight()
		return ' '.join(words), totalWeight
			
	def printGraph(self):
		for i,layer in enumerate(self.Layers):	
			print "Layer: ", i
			for j,node in enumerate(layer):
				print "Node", j
				node.printNode()


	



