import networkx as nx
from visible_view import LineOfSightVisibility, CompleteVisibility
import numpy as np

lambda_const = 0.9

class ProbOccurenceMaps:

	def __init__(self, blockHeights, enemyTeam):
		self.enemyTeam = enemyTeam
		self.poms = {enemyUnit.name : ProbOccurenceMap(blockHeights) for enemyUnit in enemyTeam.members}
		self.pomLength = len(blockHeights) * len(blockHeights[0])

	def tick(self, visibleNodes, visibleEnemyNodes):
		for enemyUnit in self.enemyTeam.members:
			pom = self.poms[enemyUnit.name]
			if enemyUnit.seenlast == 0:
				pom.clearProb()
			#for i in xrange(0, 5):
			pom.tick(visibleNodes, visibleEnemyNodes)

	def getCombinedPom(self):
		combinedPomProb = sum([pom.prob for pom in self.poms.values()])
		max_val = max(combinedPomProb)
		return np.multiply(combinedPomProb, 1.0 / max_val)
			

class ProbOccurenceMap:
    """
    A class to maintain a probabilistic occurence map of the given level
    """

    def getNodeId(self, x, y):
        return (y * self.width) + x

    def getCood(self, nodeId):
        return ((nodeId % self.width), (nodeId / self.width))

    def __init__(self, blockHeights):
        """
        Creates an occurence graph based on navigatable nodes (nodes at height 0)
        """
        self.width = len(blockHeights)
        self.height = len(blockHeights[0])
        self.g = nx.empty_graph(self.width * self.height)
        self.blockHeights = blockHeights
        self.prob = np.zeros(len(self.g.nodes())) #[0.0] * len(self.g.nodes())

        def isNavigabaleNode(nodeId):
            """ Returns false if a block is present else returns true """
            x, y = self.getCood(nodeId)
            return False if self.blockHeights[x][y] > 0 else True

        def getNeighbouringNodes(nodeId):
            """ Returns a list of nodes in all 8 directions from the given node """
            x, y = self.getCood(nodeId)
            neighbouringNodes = []
            for xoffset in range(-1, 2):
                for yoffset in range(-1, 2):
                    if xoffset == 0 and yoffset == 0:
                        continue
                    xn = x + xoffset
                    yn = y + yoffset
                    if xn < 0 or xn >= self.width or yn < 0 or yn >= self.height:
                        continue
                    neighbouringNodes.append(self.getNodeId(xn, yn))
            return neighbouringNodes

        for nodeId in self.g.nodes():
            neighbouringNodes = getNeighbouringNodes(nodeId)
            navigatableNodes = filter(isNavigabaleNode, neighbouringNodes)
            #print nodeId, len(navigatableNodes)
            self.g.add_edges_from([(nodeId, navigatableNode) for navigatableNode in navigatableNodes])

    def tick(self, visibleNodes, visibleEnemyNodes):
    	visibleNodeIds = set([self.getNodeId(int(x), int(y)) for x, y in visibleNodes])
    	visibleEnemyNodeIds = set([self.getNodeId(int(x), int(y)) for x, y in visibleEnemyNodes])

        """ Will spread probabities around the graph """
        newProb = np.zeros(len(self.prob))#[0.0] * len(self.prob)
        #print 'len =', self.g.nodes()
        for nodeId in self.g.nodes():
            neighbouringNodes = self.g.neighbors(nodeId)
            denom = 1.0 if len(neighbouringNodes) == 0 else len(neighbouringNodes)
            neighbouringProb = (lambda_const / denom) * sum([self.prob[neighbouringNodeId] for neighbouringNodeId in neighbouringNodes])
            selfProb = (1.0 - lambda_const) * self.prob[nodeId]
            newProb[nodeId] = selfProb + neighbouringProb
            #print nodeId, selfProb, neighbouringProb, newProb[nodeId]
        #print newProb
        self.prob = newProb
        """ Updates the ProbOccurenceMap based on nodes visible by a bot """
        for nodeId in visibleNodeIds:
            self.prob[nodeId] = 0.0
        for nodeId in visibleEnemyNodeIds:
            self.prob[nodeId] = 1.0

    def clearProb(self):
    	self.prob = np.zeros(len(self.prob))

