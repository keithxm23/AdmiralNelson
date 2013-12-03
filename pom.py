import networkx as nx
from visibility_wave import VisibilityWave

lambda_const = 0.5

class ProbOccurenceMap():
    """
    A class to maintain a probabilistic occurence map of the given level
    """

    def getNodeId(self, x, y):
        return (y * self.width) + x

    def getCood(self, nodeId):
        return ((nodeId % self.width), (nodeId / self.width))

    def isBlocked(self, x, y):
        return True if self.blockHeights[x][y] > 0 else False

    def setVisible(self, x, y):
        self.visibleNodes.append(self.getNodeId(x, y))

    def __init__(self, blockHeights, team, enemyTeam):
        """
        Creates an occurence graph based on navigatable nodes (nodes at height 0)
        """
        self.width = len(blockHeights)
        self.height = len(blockHeights[0])
        self.g = nx.empty_graph(self.width * self.height)
        self.blockHeights = blockHeights
        self.prob = [0] * len(self.g)
        self.visibility_wave = VisibilityWave((self.width, self.height), self.isBlocked, self.setVisible)
        self.visibleNodes = []
        self.team = team
        self.enemyTeam = enemyTeam

        def isNavigabaleNode(nodeId):
            """ Returns false if a block is present else returns true """
            x, y = self.getCood(nodeId)
            return not(self.isBlocked(x, y))

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

        for nodeId in self.g:
            neighbouringNodes = getNeighbouringNodes(nodeId)
            navigatableNodes = filter(isNavigabaleNode, neighbouringNodes)
            print nodeId, len(navigatableNodes)
            self.g.add_edges_from([(nodeId, navigatableNode) for navigatableNode in navigatableNodes])


    def tick(self):
        def update(visibleNodes, visibleEnemyNodes):
            """ Will spread probabities around the graph """
            newProb = [0] * len(self.prob)
            #print self.g.neighbors(87)
            for nodeId in self.g:
                neighbouringNodes = self.g.neighbors(nodeId)
                denom = 1 if len(neighbouringNodes) == 0 else len(neighbouringNodes)
                neighbouringProb = (lambda_const / denom) * sum([self.prob[nodeId] for nodeId in neighbouringNodes])
                selfProb = (1.0 - lambda_const) * self.prob[nodeId]
                newProb[nodeId] = selfProb + neighbouringProb
            self.prob = newProb
            """ Updates the ProbOccurenceMap based on nodes visible by a bot """
            for nodeId in visibleNodes:
                self.prob[nodeId] = 0.0
            for nodeId in visibleEnemyNodes:
                self.prob[nodeId] = 1.0

        self.visibleNodes = []
        map(self.visibility_wave.compute, [bot for bot in self.team.members if bot.state != 9]) # This call will update self.visibleNodes using a callback

        # TODO Revaluate if last know positions or current visible position to be used for pom
        #[enemyBot.position for enemyBot in teamBot.seenBy for teamBot in self.team.members]

        visibleEnemyNodeVectors = [enemyBot.position for enemyBot in self.enemyTeam.members if enemyBot.seenlast == 0.0 and enemyBot.state != 9]
        visibleEnemyNodes = [self.getNodeId(int(vec.x), int(vec.y)) for vec in visibleEnemyNodeVectors]

        update(self.visibleNodes, visibleEnemyNodes)

