import nextworkx as nx

lambda_const = 0.2

class pog:
    def __init__(self, blockHeights):
        self.width = len(blockHeights)
        self.height = len(blockHeights[0])
        self.g = nx.empty_graph(self.width * self.height)
        self.blockHeights = blockHeights
        self.prob = [] * len(g)

        for nodeId in self.g:
            neighbouringNodes = getNeighbouringNodes(nodeId)
            navigatableNodes = filter(isNavigabaleNode, neighbouringNodes)
            self.g.add_edges_from([(nodeId, navigatableNode) for navigatableNode in navigatableNodes])
            self.prob[nodeId] = 0.0

    def update(visibleNodes, visibleEnemyNodes):
        tick()
        for nodeId in visibleNodes:
            self.prob[nodeId] = 0.0
        for nodeId in visibleEnemyNodes:
            self.prob[nodeId] = 1.0

    def tick():
        newProb = [] * len(self.prob)
        for nodeId in self.g:
            neighbouringNodes = self.g.neighbours(nodeId)
            neighbouringProb = (lambda_const / 8.0) * sum([self.prob[nodeId] for nodeId in neighbouringNodes])
            selfProb = (1.0 - lambda_const) * self.prob[nodeId]
            newProb[nodeId] = selfProb + neighbouringProb
        self.prob = newProb

    def getNeighbouringNodes(nodeId):
        x, y = getCood(nodeId)
        neighbouringNodes = []
        for xoffset in range(-1, 1):
            for yoffset in range(-1, 1):
                if xoffset == 0 and yoffset == 0:
                    continue
                xn = x + xoffset
                yn = y + yoffset
                if xn < 0 or xn >= self.width or yn < 0 or yn >= self.height:
                    continue
                neighbouringNodes.append(getNodeId(xn, yn))
        return neighbouringNodes

    def isNavigabaleNode(nodeId):
        x, y = getCood(nodeId)
        return False if self.blockHeights[y][x] > 0 else True

    def getNodeId(x, y):
        return (y * self.width) + x

    def getCood(nodeId):
        return ((nodeId % self.width), (nodeId / self.width))