""""
http://www.laurentluce.com/posts/solving-mazes-using-python-simple-recursivity-and-a-search/
"""

import heapq
from game_constants import gameplayDataFilepath

class Cell(object):
    def __init__(self, x, y, reachable, g):
        """
        Initialize new cell

        @param x cell x coordinate
        @param y cell y coordinate
        @param reachable is cell reachable? not a wall?
        """
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0


class AStar(object):
    def __init__(self, blockHeights, visibility_map):
        self.op = []        #Open List
        heapq.heapify(self.op)
        self.cl = set()     #Closed List
        self.cells = []     #Flattened list of all cells in grid
        self.gridHeight = len(blockHeights[0])
        self.gridWidth = len(blockHeights)

        for x in range(self.gridWidth):
            for y in range(self.gridHeight):
                if blockHeights[x][y] > 0.0:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable, visibility_map[x][y]))


    def get_heuristic(self, cell):
        """
        Compute the heuristic value H for a cell: Manhattan distance between
        this cell and the ending cell multiply by 10.

        @param cell
        @returns heuristic value H
        """
        return abs(cell.x - self.end.x) + abs(cell.y - self.end.y)


    def get_cell(self, x, y):
        """
        Returns a cell from the cells list

        @param x cell x coordinate
        @param y cell y coordinate
        @returns cell
        """
        return self.cells[x * self.gridHeight + y]


    def get_adjacent_cells(self, cell):
        """
        Returns adjacent cells to a cell. Clockwise starting
        from the one on the right.

        @param cell get adjacent cells for this cell
        @returns adjacent cells list
        """
        cells = []
        if cell.x < self.gridWidth-1:       #Right cell
            cells.append(self.get_cell(cell.x+1, cell.y))
            if cell.y < self.gridHeight-1:  #Bottom-Right cell
                cells.append(self.get_cell(cell.x+1, cell.y+1))
        if cell.y < self.gridHeight-1:      #Bottom cell
            cells.append(self.get_cell(cell.x, cell.y+1))
            if cell.x > 0:                  #Bottom-Left cell
                cells.append(self.get_cell(cell.x-1, cell.y+1))
        if cell.x > 0:                      #Left cell
            cells.append(self.get_cell(cell.x-1, cell.y))
            if cell.y > 0:                  #Top-Left cell
                cells.append(self.get_cell(cell.x-1, cell.y-1))
        if cell.y > 0:                      #Top cell
            cells.append(self.get_cell(cell.x, cell.y-1))
            if cell.x < self.gridWidth-1:   #Top-Right cell
                cells.append(self.get_cell(cell.x+1, cell.y-1))

        return cells


    def display_path(self):
        """
        Returns a list of (x,y) coordinates which lie in path to destination
        """
        path = []
        cell = self.end
        path.append((cell.x, cell.y))
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x, cell.y))
            #print 'path: cell: %d,%d' % (cell.x, cell.y)

        path.reverse()
        return path

    def update_cell(self, adj, cell):
        """
        Update adjacent cell

        @param adj adjacent cell to current cell
        @param cell current cell being processed
        """
        adj.g = cell.g
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g


    def get_path(self, startx, starty, endx, endy):
        path = []
        if startx == endx and starty == endy:
            return path

        self.start = self.get_cell(startx, starty)
        self.end = self.get_cell(endx, endy)
        # add starting cell to open heap queue
        heapq.heappush(self.op, (self.start.f, self.start))
        while len(self.op):
            # pop cell from heap queue
            f, cell = heapq.heappop(self.op)
            #print cell.x,cell.y
            # add cell to closed list so we don't process it twice
            self.cl.add(cell)
            # if ending cell, display found path
            if cell is self.end:
                path = self.display_path()
                break
            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells(cell)
            for c in adj_cells:
                if c.reachable and c not in self.cl:
                    if (c.f, c) in self.op:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found for this adj
                        # cell.
                        if c.g > cell.g + 10:
                            self.update_cell(c, cell)
                    else:
                        self.update_cell(c, cell)
                        # add adj cell to open list
                        heapq.heappush(self.op, (c.f, c))

        #Reset for next search
        self.op = []        #Open List
        heapq.heapify(self.op)
        self.cl = set()     #Closed List

        return path


import cPickle as pickle
from visibility import get_visibility_map
gamedata = pickle.load(open(gameplayDataFilepath, 'rb'))
blockHeights = gamedata['blockHeights']
vis_map = get_visibility_map(blockHeights)
astar = AStar(blockHeights, vis_map.tolist())