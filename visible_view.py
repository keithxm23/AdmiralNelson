from itertools import izip
from math import floor, copysign
import math
import networkx as nx
from api.vector2 import Vector2

sign = lambda x: int(copysign(1, x))

def line(A, B, finite = True):
    """
    Modified version of Alex J. Champandard's line function

    This function is a generator that returns grid coordinates along a line
    between points A and B.  It uses a floating-point version of the Bresenham
    algorithm, which is designed to be sub-pixel accurate rather than assuming
    the middle of each pixel.  This could most likely be optimized further using
    Bresenham's integer techniques.

    @param finite   You can specify a line that goes only between A or B, or
                    infinitely from A beyond B.
    """
    d = B - A           # Total delta of the line.

    if abs(d.x) >= abs(d.y):
        sy = d.y / abs(d.x)     # Slope along Y that was chosen.
        sx = sign(d.x)          # Step in the correct X direction.

        y = int(floor(A.y))     # Starting pixel, rounded.
        x = int(floor(A.x))
        e = A.y - float(y)      # Exact error calculated.

        while True:
            yield (x, y)
            if finite and x == int(floor(B.x)):
                break
            p = e           # Store current error for reference.
            e += sy         # Accumulate error from slope.
            if e >= 1.0:    # Reached the next row yet?
                e -= 1.0        # Re-adjust the error accordingly.
                y += 1          # Step the coordinate to next row.
            elif e < 0.0:   # Reached the previous row?
                e += 1.0        # Re-adjust error accordingly.
                y -= 1          # Step the coordinate to previous row.
            x += sx         # Take then next step with x.

    else: # abs(d.x) < abs(d.y)
        sx = d.x / abs(d.y)     # Slope along Y that was chosen.
        sy = sign(d.y)          # Step in the correct X direction.

        x = int(floor(A.x))     # Starting pixel, rounded.
        y = int(floor(A.y))
        e = A.x - float(x)      # Exact error calculated.
 
        while True:
            yield (x, y)
            if finite and y == int(floor(B.y)):
                break
            p = e           # Store current error for reference.
            e += sx         # Accumulate error from slope.

            if e >= 1.0:    # Reached the next row yet?
                e -= 1.0        # Re-adjust the error accordingly.
                x += 1          # Step the coordinate to next column.
            elif e < 0.0:   # Reached the previous row?
                e += 1.0        # Re-adjust error accordingly.
                x -= 1          # Step coordinate to the previous column.
            y += sy         # Go for another iteration with next Y.

class VisibleView:

    def isBlocked(self, x, y):
        return True if self.blockHeights[x][y] > 1 else False

    def setVisible(self, x, y):
        self.visibleNodes.append((x, y))

    def __init__(self, fieldOfViewAngles, blockHeights, team, enemyTeam):
        width = len(blockHeights)
        height = len(blockHeights[0])
        self.blockHeights = blockHeights
        self.visibleNodes = []
        self.team = team
        self.enemyTeam = enemyTeam
        self.visibility_view = LineOfSightVisibility((width, height), fieldOfViewAngles, self.isBlocked, self.setVisible)

    def tick(self):
        self.visibleNodes = []
        #This call will update self.visibleNodes using a callback
        map(self.visibility_view.compute, [bot for bot in self.team.members if bot.state != 9])
        visibleEnemyNodes = [(enemyBot.position.x, enemyBot.position.y) for enemyBot in self.enemyTeam.members if enemyBot.seenlast < 1 and enemyBot.state != 9]
        return (self.visibleNodes, visibleEnemyNodes)



class LineOfSightVisibility:
    """
    Class to compute what is visible from a bots perspective based on position, direction
    and field of view
    """
    def __init__(self, (width, height), fieldOfViewAngles, isBlocked, setVisible):
        self.width = width
        self.height = height
        self.fieldOfViewAngles = fieldOfViewAngles
        self.isBlocked = isBlocked
        self.setVisible = setVisible
        self.borderGraph = self.generateBorderGraph(width, height)

    def generateBorderGraph(self, width, height):
        """ Precomputes a graph containing the border coordinate for the level given.
            Meant to be used for ray casting to these points.
        """
        nodes = [(x, 0) for x in xrange(0, width)]
        nodes.extend([(width - 1, y) for y in xrange(1, height)])
        nodes.extend([(x, height - 1) for x in xrange(width - 2, -1, -1)])
        nodes.extend([(0, y) for y in xrange(height - 2, -1, -1)])

        borderGraph = nx.Graph()
        for index in xrange(0, len(nodes) - 1):
            borderGraph.add_edge(nodes[index], nodes[index + 1])
        return borderGraph

    def findEndpoints(self, pos, direc, viewAngle):
        upperEndpoint, staightEndpoint, lowerEndpoint = self.findArcEndPoints(pos, direc, viewAngle)
        endpoints = nx.shortest_path(self.borderGraph, upperEndpoint, staightEndpoint)
        endpoints.extend(nx.shortest_path(self.borderGraph, staightEndpoint, lowerEndpoint))
        return endpoints

    def findArcEndPoints(self, pos, direc, viewAngle):
        upperDirecVector = self.rotate(direc, viewAngle / 2.0)
        lowerDirecVector = self.rotate(direc, -viewAngle / 2.0)
        upperProjection = line(pos, pos + upperDirecVector, finite = False)
        strightProjection = line(pos, pos + direc, finite = False)
        lowerProjection = line(pos, pos + lowerDirecVector, finite = False)
        return map(self.getLineEndpoint, [upperProjection, strightProjection, lowerProjection])

    def rotate(self, vec, angle):
        cos = math.cos(angle)
        sin = math.sin(angle)
        x = (vec.x * cos) - (vec.y * sin)
        y = (vec.y * cos) + (vec.x * sin)
        return Vector2(x, y)
        
    def getLineEndpoint(self, line):
        endpoints = set(self.borderGraph.nodes())
        for x, y in line:
            if (x, y) in endpoints: break
        return (x, y)

    def compute(self, botInfo):
        pos = botInfo.position
        direc = botInfo.facingDirection
        viewAngle = self.fieldOfViewAngles[botInfo.state]
        endpoints = self.findEndpoints(pos, direc, viewAngle)
        
        for endpointX, endpointY in endpoints:
            endpoint = Vector2(endpointX, endpointY)
            for x, y in line(pos, endpoint, finite = True):
                if self.isBlocked(x, y):
                    break
                self.setVisible(x, y)

class CompleteVisibility(object):
    """
    Provides 360 degrees visibility for each bot.

    Modified version of Alex J. Champandard's visibilityWave

    Can calculate all visible cells from a
    single cell.  It starts from a specified point and "flood fills" cells that
    are visible in four different directions.  Each direction of the visibility
    wave is bounded by two lines, which are then rasterized in between.  If
    obstacles are encountered, the wave is split into sub-waves as necessary.
    """

    def __init__(self, (width, height), fieldOfViewAngles, isBlocked, setVisible):
        self.width = width
        self.height = height
        self.isBlocked = isBlocked
        self.setVisible = setVisible

    def xwave_internal(self, p, upper, lower, direction):
        """Propagate a visibility wave along one direction with X-major axis."""

        for (ux, uy), (lx, ly) in izip(upper, lower):
            assert ux == lx, "{} != {}".format(ux, lx)
            x = ux
            # If the upper and lower bounds are switched, just swap them.
            if uy > ly: uy, ly = ly, uy

            # Check if the wave has stepped out of bounds.
            if x < 0: break
            if x >= self.width: break

            waves = []
            visible = []
            blocks = False

            # Now iterate through all the pixels in this column.
            for y in range(max(uy, 0), min(ly+1, self.height)):

                # If a free cell is encountered, store it for later.
                if not self.isBlocked(x, y):
                    visible.append((x, y))
                    self.setVisible(x, y)
                # If the cell is blocked, then we keep track of the entire span of cells.
                else:
                    blocks = True
                    if visible:
                        waves.append(visible)
                        visible = []
                    else:
                        pass
        
            # Now we have a list of all the visible spans of cells, for sub-waves.
            if visible:
                waves.append(visible)
                visible = []

            # Split the wave into sub-waves if there were blocks.
            if blocks:
                for i, w in enumerate(waves):
                    # Calculate the coordinates of the start and end of the new wave.
                    w0, wn = Vector2(w[0][0]+0.5, w[0][1]+0.5), Vector2(w[-1][0]+0.5, w[-1][1]+0.5)
                    u = w0 - p
                    l = wn - p
                    u = u / abs(u.x)
                    l = l / abs(l.x)

                    # Adjustment for error case dy>dx is caused by sub-pixel drift.
                    if abs(u.y)>abs(u.x): u.y=abs(u.x)*sign(u.y)
                    if abs(l.y)>abs(l.x): l.y=abs(l.x)*sign(l.y)
                    w0 += u
                    wn += l

                    # If this wave cell is the first or last, we use the exact same line equation.
                    if i>0 or w[0][1] > max(uy, 0):
                        uppr = line(w0, w0+u, finite = False)
                    else:
                        uppr = upper
                    if i<len(waves)-1 or w[-1][1] < min(ly+1, self.height)-1:
                        lowr = line(wn, wn+l, finite = False)
                    else:
                        lowr = lower

                    # Now recursively handle this case, propagating the sub-wave further.
                    self.xwave_internal(p, uppr, lowr, direction)
                return

    def ywave_internal(self, p, upper, lower, direction):
        for (ux, uy), (lx, ly) in izip(upper, lower):
            assert uy == ly, "{} != {}".format(uy, ly)
            y = uy

            if ux > lx: ux, lx = lx, ux

            if y < 0: break
            if y >= self.height: break

            waves = []
            visible = []
            blocks = False
            for x in range(max(ux, 0), min(lx+1, self.width)):
                if self.isBlocked(x, y):
                    blocks = True
                    if visible:
                        waves.append(visible)
                        visible = []
                    else:
                        pass
                else:
                    visible.append((x,y))
                    self.setVisible(x, y)
        
            if visible:
                waves.append(visible)
                visible = []

            if blocks:
                for i, w in enumerate(waves):
                    w0, wn = Vector2(w[0][0]+0.5, w[0][1]+0.5), Vector2(w[-1][0]+0.5, w[-1][1]+0.5)
                    u = w0 - p
                    l = wn - p
                    u = u / abs(u.y)
                    l = l / abs(l.y)

                    if abs(u.x)>abs(u.y): u.x=abs(u.y)*sign(u.x)
                    if abs(l.x)>abs(l.y): l.x=abs(l.y)*sign(l.x)
                    w0 += u
                    wn += l
                    if i>0 or w[0][0] > max(ux, 0):
                        uppr = line(w0, w0+u, finite = False)
                    else:
                        uppr = upper
                    if i<len(waves)-1 or w[-1][0] < min(lx+1, self.width)-1:
                        lowr = line(wn, wn+l, finite = False)
                    else:
                        lowr = lower

                    self.ywave_internal(p, uppr, lowr, direction)
                return

    def compute(self, botInfo):
        """Propagate four visibility waves, along X and Y both positive and negative."""

        p = botInfo.position

        if self.isBlocked(int(p.x), int(p.y)):
            return

        # TODO Fix this. Waves are generated in every direction, should instead be generated
        # only in the direction being faced
        upper = line(p, p+Vector2(+0.5, -0.5), finite = False)
        lower = line(p, p+Vector2(+0.5, +0.5), finite = False)
        self.xwave_internal(p, upper, lower, Vector2(+1.0, 0.0))

        upper = line(p, p+Vector2(-0.5, -0.5), finite = False)
        lower = line(p, p+Vector2(-0.5, +0.5), finite = False)

        upper.next(), lower.next()
        self.xwave_internal(p, upper, lower, Vector2(-1.0, 0.0))

        p0 = p + Vector2(0.0, -1.0)
        upper = line(p0, p0+Vector2(-0.5, -0.5), finite = False)
        lower = line(p0, p0+Vector2(+0.5, -0.5), finite = False)
        self.ywave_internal(p, upper, lower, Vector2(0.0, -1.0))

        p1 = p + Vector2(0.0, +1.0)
        upper = line(p1, p1+Vector2(-0.5, +0.5), finite = False)
        lower = line(p1, p1+Vector2(+0.5, +0.5), finite = False)
        self.ywave_internal(p, upper, lower, Vector2(0.0, +1.0))

