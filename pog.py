import nextworkx as nx


class pog:

	def __init__(self, blockHeights):
		self.width = len(blockHeights)
		self.height = len(blockHeights[0])
		self.g = nx.empty_graph(self.width * self.height)
		self.blockHeights = blockHeights

		for nodeId in g:
			neighbouringNodes = getNeighbouringNodes(nodeId)
			navigatableNodes = filter(isNavigabaleNode, neighbouringNodes)
			g.add_edges_from([(nodeId, navigatableNode) for navigatableNode in navigatableNodes])


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