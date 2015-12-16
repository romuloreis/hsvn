#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#Import the libriraies
import fnss
import networkx as nx

#Create SN
#Read the Topology from the BRITE file
topology = fnss.parse_brite("bigSN.brite")

#Set weight to 1
fnss.set_weights_constant(topology, 1)

#Create a Grapth based on the topology read
SN = nx.Graph(topology)

for n in SN.nodes():
	SN.node[n]['sync'] = False
	SN.node[n]['max_cpu'] = 100
	SN.node[n]['cur_cpu'] = 100
	SN.node[n]['idle'] = True

for u, v in SN.edges():
	SN.edge[u][v]['sync'] = False
	SN.edge[u][v]['max_bw'] = 1000
	SN.edge[u][v]['cur_bw'] = 1000

#Create Virtual Network 1
topology = fnss.parse_brite("VN1.brite")

#Set weight to 1
fnss.set_weights_constant(topology, 1)

#Create a Grapth based on the topology read
VN1 = nx.Graph(topology)

for n in VN1.nodes():
	VN1.node[n]['sync'] = False
	VN1.node[n]['cpu']=10
	VN1.node[n]['mapped'] = False
	VN1.node[n]['physicalNode'] = None
	VN1.node[n]['idle'] = False

for u, v in VN1.edges():
	VN1.edge[u][v]['sync'] = False
	VN1.edge[u][v]['weight'] = 1
	VN1.edge[u][v]['bw'] = 100
	VN1.edge[u][v]['mapped'] = False
	VN1.edge[u][v]['physicalPath'] = None


#Create Virtual Network 2
topology = fnss.parse_brite("VN2.brite")

#Set weight to 1
fnss.set_weights_constant(topology, 1)

#Create a Grapth based on the topology read
VN2 = nx.Graph(topology)

for n in VN2.nodes():
	VN2.node[n]['sync'] = False
	VN2.node[n]['cpu']=10
	VN2.node[n]['mapped'] = False
	VN2.node[n]['physicalNode'] = None
	VN2.node[n]['idle'] = False

for u, v in VN2.edges():
	VN2.edge[u][v]['sync'] = False
	VN2.edge[u][v]['weight'] = 1
	VN2.edge[u][v]['bw'] = 100
	VN2.edge[u][v]['mapped'] = False
	VN2.edge[u][v]['physicalPath'] = None

#Create a list of VNs
VNList = [VN1, VN2]

"""
avaiablectyfyt
iojoijtrdtr
"""

##################FIND CANDIDATES
#Return the Sync Node with more CPU capacity current avaiable
def getSyncFirstFit(virtualNode, substrateNetwork):
	#First, set firstFit as None
	firstFit = None
	nodeAvaiable = False
	#For each node in the substrate network do
	for n in substrateNetwork.nodes():
		#If empity, set worstFit with the first node in the list, just for having a reference
		if not firstFit:
			firstFit = substrateNetwork.node[n]
		#else, verify sync
		if substrateNetwork.node[n]['sync'] is True:
			#verify if it has enough cpu capacity
			if substrateNetwork.node[n]['cur_cpu'] >= virtualNode.get('cpu'):
				#Set bestFit with the node with more CPU capacity
				if substrateNetwork.node[n]['cur_cpu'] >= firstFit.get('cur_cpu'):
					firstFit = substrateNetwork.node[n]
					nodeAvaiable = True
	if nodeAvaiable:
		return firstFit
	else:
		return None


#Return the Sync Node with more CPU capacity current avaiable
def getAsyncFirstFit(virtualNode, substrateNetwork):
	#First, set firstFit as None
	firstFit = None
	nodeAvaiable = False
	#For each node in the substrate network do
	for n in substrateNetwork.nodes():
		#If empity, set worstFit with the first node in the list, just for having a reference
		if not firstFit:
			firstFit = substrateNetwork.node[n]
		#else, verify sync
		if substrateNetwork.node[n]['sync'] is False:
			#verify if it has enough cpu capacity
			if substrateNetwork.node[n]['cur_cpu'] >= virtualNode.get('cpu'):
				#Set bestFit with the node with more CPU capacity
				if substrateNetwork.node[n]['cur_cpu'] >= firstFit.get('cur_cpu'):
					firstFit = substrateNetwork.node[n]
					nodeAvaiable = True
	if nodeAvaiable:
		return firstFit
	else:
		return None

############################MAP NODES
def mapSyncNodes(virtualNetwork, substrateNetwork):
	bestFit = None
	#for each VNode in VN
	for vn in virtualNetwork.nodes():
		if virtualNetwork.node[vn]['sync'] is True:
			#get the FIRST IDLE SYNC physical NODE 
			#bestFitVertex = HSVN.findFirstBestFitSyncVertex(physicalGraph, virtualGraph.getVertexes().get(i));
			bestFit = getSyncFirstFit(virtualNetwork.node[vn], substrateNetwork)
			#return None if there is no one
			if bestFit is not None:
				#for each SYNC physical NODE
				for pn in substrateNetwork.nodes():
					#if the physical node is sync...
					if substrateNetwork.node[pn]['sync'] is True:
						#if the physical node is idle...
						if substrateNetwork.node[pn]['idle'] is True:
							#if the physical node has enough CPU capacity (weight)...
							if substrateNetwork.node[pn]['cur_cpu'] >=  virtualNetwork.node[vn]['cpu']:
								#if the physical node has less CPU capacity (weight)...than the candidate
								if substrateNetwork.node[pn]['cur_cpu'] <= bestFit.get('cur_cpu'):
								#This physical node become the new bestFit node
									besFit = substrateNetwork.node[pn]

			#after for each physical node...
			#if bestFit is not None
			if bestFit is not None:
				#virtual node is mapped on the best fit..
				virtualNetwork.node[vn]['physicalNode'] = bestFit
				#the physical node "best fit" has the CPU capacity reduced
				besFit['cur_cpu'] = (besFit['cur_cpu'] - virtualNetwork.node[vn]['cpu'])
				#AAAAAAAAAA virtualNetwork.node[vn]['physicalNode'].set(cur_cpu - virtualNetwork.node[vn]['cpu'])
				#here it happens the mapping process... now the virutal node knows where it is mapped
				#set the physical node as NO IDLE (BUSY)
				bestFit['idle'] = False
				return True
			else:
				#Tehre is no avaiable Physical Node
				return False



def mapAsyncNodes(virtualNetwork, substrateNetwork):
	bestFit = None
	#for each VNode in VN
	for vn in virtualNetwork.nodes():
		if virtualNetwork.node[vn]['sync'] is False:
			#get the FIRST IDLE SYNC physical NODE 
			#bestFitVertex = HSVN.findFirstBestFitSyncVertex(physicalGraph, virtualGraph.getVertexes().get(i));
			bestFit = getAsyncFirstFit(virtualNetwork.node[vn], substrateNetwork)
			#return None if there is no one
			if bestFit is not None:
				#for each SYNC physical NODE
				for pn in substrateNetwork.nodes():
					#if the physical node is sync...
					if substrateNetwork.node[pn]['sync'] is False:
						#if the physical node is idle...
						if substrateNetwork.node[pn]['idle'] is True:
							#if the physical node has enough CPU capacity (weight)...
							if substrateNetwork.node[pn]['cur_cpu'] >=  virtualNetwork.node[vn]['cpu']:
								#if the physical node has less CPU capacity (weight)...than the candidate
								if substrateNetwork.node[pn]['cur_cpu'] <= bestFit.get('cur_cpu'):
								#This physical node become the new bestFit node
									besFit = substrateNetwork.node[pn]


			#after for each physical node...
			#if bestFit is not None
			if bestFit is not None:
				#virtual node is mapped on the best fit..
				virtualNetwork.node[vn]['physicalNode'] = bestFit
				#the physical node "best fit" has the CPU capacity reduced
				besFit['cur_cpu'] = (besFit['cur_cpu'] - virtualNetwork.node[vn]['cpu'])
				#AAAAAAAAAA virtualNetwork.node[vn]['physicalNode'].set(cur_cpu - virtualNetwork.node[vn]['cpu'])
				#here it happens the mapping process... now the virutal node knows where it is mapped
				#set the physical node as NO IDLE (BUSY)
				bestFit['idle'] = False
				return True
			else:
				bestFit = getSyncFirstFit(virtualNetwork.node[vn], substrateNetwork)
				#return None if there is no one
				if bestFit is not None:
					#for each SYNC physical NODE
					for pn in substrateNetwork.nodes():
						#if the physical node is sync...
						if substrateNetwork.node[pn]['sync'] is True:
							#if the physical node is idle...
							if substrateNetwork.node[pn]['idle'] is True:
								#if the physical node has enough CPU capacity (weight)...
								if substrateNetwork.node[pn]['cur_cpu'] >=  virtualNetwork.node[vn]['cpu']:
									#if the physical node has less CPU capacity (weight)...than the candidate
									if substrateNetwork.node[pn]['cur_cpu'] <= bestFit.get('cur_cpu'):
									#This physical node become the new bestFit node
										besFit = substrateNetwork.node[pn]

				#after for each physical node...
				#if bestFit is not None
				if bestFit is not None:
					#virtual node is mapped on the best fit..
					virtualNetwork.node[vn]['physicalNode'] = bestFit
					#the physical node "best fit" has the CPU capacity reduced
					besFit['cur_cpu'] = (besFit['cur_cpu'] - virtualNetwork.node[vn]['cpu'])
					#AAAAAAAAAA virtualNetwork.node[vn]['physicalNode'].set(cur_cpu - virtualNetwork.node[vn]['cpu'])
					#here it happens the mapping process... now the virutal node knows where it is mapped
					#set the physical node as NO IDLE (BUSY)
					bestFit['idle'] = False
					return True
				else:
					#There is no avaiable Physical Node
					return False

#mapAsyncNodes()+++++

def releaseResources(substrateNetwork):
	for n in substrateNetwork.nodes():
		substrateNetwork.node[n]['idle'] = True


def mapVirtualNodes(virtualNetwork, substrateNetwork):
    if mapSyncNodes(virtualNetwork, substrateNetwork) is True:
    	print("Todos os nodos Sync foram mapeados com sucesso")
    if mapAsyncNodes(virtualNetwork, substrateNetwork) is True:
    	print("Todos os nodos Async foram mapeados com sucesso")
        #seta idle = true for all physical nodes
        releaseResources(substrateNetwork)
        return True;
    else:
        print("Mapeamento dos nodos n efetuado")
        #Free unused resources
        #freeUnusedNodeResources(virtualGraph, physicalGraph)###############################################
        #seta idle = true for all physical nodes
        releaseResources(substrateNetwork)
        return False;

"""
bestPath=None
paths = nx.single_source_dijkstra_path(SN, 1, weight='weight')
bw=0

for path in paths.values():
	validPath = True
	lastNode = None
	for node in path:
		#print "path: ", path, " node ", node
		if not lastNode:
			lastNode = node
			if not SN.node[node]['sync']:
				validPath = False
		else:
			#print SN.edge[lastNode][node]
			if SN.edge[lastNode][node]['cur_bw'] <= bw:
				validPath = False
			if not SN.edge[lastNode][node]['sync']:
				validPath = False
			if not SN.node[node]['sync']:
				validPath = False
			lastNode = node
	if validPath:
		if not bestPath:
			bestPath=path
		else:
			if len(bestPath) >= len(path):
				bestPath = path

		print "end"#paths[path]['valid']=True
print bestPath
"""
#########MAIN#############
#For each vn in the list do
for vn in VNList:
	factor = 0
	for n in vn.nodes():
		factor += vn.node[n]['cpu']
	vn.graph['factor'] = factor

#Re-order
#For each vn in the list do
for vn in VNList:
	mapVirtualNodes(vn, SN)



#valid
#sync
#def isValid(path):