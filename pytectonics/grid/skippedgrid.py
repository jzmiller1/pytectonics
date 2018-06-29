from math import sin, cos, asin, pi, sqrt, log, floor
from scipy.constants import golden #golden ratio
import itertools

def sign(n):
    """Returns 1 for positive, -1 for negative, and 0 for 0"""
    return 0 if not n else n/abs(n)
def inclusive(start, stop): 
    """Custom variant of xrange covering range [a,b], not [a,b)"""
    return xrange(start, stop+1)
class SkippedGrid:
    '''All implementation details are based upon Kurihara 1965'''
    def __init__(self, avgDistance):
        self.avgDistance = avgDistance
        self.numLat = SkippedGrid.getNumLat(avgDistance)
        self.totalPointNum = SkippedGrid.getPointNum(self.numLat)
        self._init_coverage()
    def _init_coverage(self):
        self.coverage = [[[] for i in inclusive(0, SkippedGrid.getNumLon(j))]
                             for j in inclusive(-self.numLat,self.numLat)]
    def __iter__(self):
        return self.getPoints()
    def __len__(self):
        return sum([len(cell) 
                    for lat in self.coverage 
                    for cell in lat])
    def __getitem__(self, key):
        i, j = key
        #print key, len(self.coverage[j+self.numLat])
        return self.coverage[j+self.numLat][i]
    def __setitem__(self, key, val):
        i, j = key
        self.coverage[j+self.numLat][i] = val
    def getIndex(self, point):
        lat, lon = point
        #print lat, lon
        j=max(1, round((1-abs(lat/(pi/2)))*self.numLat ))
        assert j != 0.0
        i=((lon/(pi/2))*(j)) % (self.getNumLon(j))
        #print i, j
        if j <= self.numLat: j *= sign(lat)
        id =  int(round(i)), int(j)
        return id
    def _getLat(self, (i,j)):
        return (pi/2)*(1-float(abs(j))/self.numLat) * sign(j)
    def _getLon(self, (i,j)):
        return (pi/2)*(float(i)/float(abs(j)))%(2*pi)
    def getCoordinates(self, index):
        return (self._getLat(index), self._getLon(index))
    def getNeighborCells(self, (i,j), iOffsets=[-1, 0, 1], jOffsets=[-1,0,1]):
        '''Returns indices occupying cells neighboring the cell specified by index.'''
        for iOffset, jOffset in itertools.product(iOffsets, jOffsets):
            jnew = j+jOffset
            if jnew == 0: continue
            if abs(jnew) > self.numLat: continue
            
            inew = (i+iOffset) % self.getNumLon(jnew)
            yield (inew, jnew)
    def getCellNeighbors(self, index):
        '''Returns points occupying cells neighboring the cell specified by index'''
        return itertools.chain.from_iterable([self[neighborIndex] 
                                              for neighborIndex in self.getNeighborCells(index)])
    def getIndices(self):
        #for j in xrange(1,10):
        #    for i in xrange(0, 4*j-4):
        #        if abs(j) != 1:
        #            yield (i,j)
        return [(i,j) 
                for j in inclusive(-self.numLat,self.numLat) if j != 0
                for i in inclusive(0, SkippedGrid.getNumLon(j))]
    def getCells(self):
        for i in self.getIndices():
            yield self[i]
    def getPoints(self):
        for cell in self.getCells():
            for point in cell:
                yield point
    def getOverlappedCells(self, overlapNum):
        for i in self.getIndices():
            if len(self[i])>overlapNum:
                yield self[i]
    def getEmptyCells(self, filter):
        cells = [i for i in self.getIndices() 
                 if len([point for point in self[i]
                         if filter(point)])<=0]
        return cells
    
    
    def add(self, point):
        self[point.id].append(point)
    def remove(self, point):
        self[point.id].remove(point)
    def update(self):
        cells = self.coverage
        self._init_coverage()
        for lat in cells:
            for cell in lat:
                for point in cell:
                    point.id = self.getIndex(point)
                    self[point.id].append(point)
    def getNeighbors(self, point):
        return self.getCellNeighbors(point.id) +            \
               [other for other in self[point.id] 
                      if other != point]
    def getNearest(self, point, points, maxDistance = float('inf'), greedy=False):
        if not points: return None
        closest = None
        closestDistance = float('inf')
        for other in points:
            distance = point.getDistance(other)
            if distance < maxDistance:
                if greedy: return other
                elif distance < closestDistance:
                    closest = other
                    closestDistance = distance
        return closest
        nearest = min(points, key=point.getDistance)
        if maxDistance and point.getDistance(nearest) > maxDistance: return None 
        return nearest
    def getNearestPairs(self):
        raise NotImplementedError()
    def getNearestWith(self, points):
        raise NotImplementedError()
    def getFurthest(self, point):
        raise NotImplementedError()
    def getFurthestPairs(self, point):
        raise NotImplementedError()
    def getFurthestWith(self, points):
        raise NotImplementedError()
        
        
    @staticmethod
    def getPointNum(numLat):
        return 4 * numLat**2 + 2
    @staticmethod
    def getNumLat(avgAngleDistance):
        return int(pi / avgAngleDistance)
    @staticmethod 
    def getNumLon(j):
        return 4*(abs(j))