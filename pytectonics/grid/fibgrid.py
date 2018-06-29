from math import sin, cos, asin, log
from itertools import product
from cartesianarray import CartesianArray
from pytectonics.utils import *
from visual import frame, vector

class FibGrid:
    '''Represents a grid of evenly distributed cells upon a sphere.
    Cells are positioned in a pattern resembling the seeds on a sunflower,
    ultimately based upon the golden ratio / the fibonacci sequence.
    This approach allows for any number of cells to be evenly and efficiently
    distributed on a sphere.
    GeoCoordinates may be placed upon the grid and are indexed using a 
    coordinate system specific to this style of grid. This allows for fast
    geospatial lookups 
    All implementation details are based upon Swinbank & Purser 2006'''
    
    #---STATIC METHODS
    @staticmethod
    def getPointNum(avgAngleDistance):
        #Ideally, we want all distances to be the same.
        #This would require each face on the polyhedron 
        #to be an equilateral triangle. 
        #with edge length = minDistance
        #First, find the area of one of those equilateral triangles
        faceArea =  sqrt(3)/4 * avgAngleDistance**2
        #zIncrement = faceArea / (2*pi)
        #return 2/zIncrement
        #The area of our sphere is a constant:
        sphereArea = 4*pi
        totalPointNum = sphereArea/faceArea
        pointNum = totalPointNum-1 / 2
        return int(pointNum)

    #---MAGIC METHODS
    def __init__(self, avgDistance, mapping=None):
        self.avgDistance = avgDistance
        self.pointNum = FibGrid.getPointNum(avgDistance)
        self.totalPointNum = 2*self.pointNum+1
        self.zIncrement = 2.0 / self.totalPointNum
        
        self.coverage = [None for i in xrange(0, self.totalPointNum)]
        
        self.resolution = 5
        if not mapping:
            mapping = CartesianArray(SEMICIRCLE / avgDistance * self.resolution,
                                         CIRCLE / avgDistance * self.resolution)
            for i, j in mapping.getIds():
                lat, lon = mapping.idToPos((i, j))
                mapping.array[i,j] = self._getIndex((lat, lon))
        self.mapping = mapping
                
        self.frame = frame(visible = False)
        
        self.points = [None for i in xrange(0, self.totalPointNum)]
        for i in self.getIndices():
            self.points[i] = toCartesian(self._getSpherical(i))
            
    def __iter__(self):
        for cell in self.coverage:
            if cell: yield cell
    def __len__(self):
        return len([cell for cell in self.coverage if cell])
    def __in__(self, crust):
        return self.coverage[crust.id] is not None
    def __getitem__(self, key):
        return self.coverage[key]
    def __setitem__(self, key, val):
        self.coverage[key] = val
        
    #---GET INDEX FUNCTIONS
    def _getZone(self, lat, approx=round):
        zone = log(self.totalPointNum * \
                   pi * sqrt5 * cos(lat)**2, 
                   phi) / 2.0
        return int(approx(zone))
    def _getZoneIndex(self, z, approx=round):
        return approx(z /self.zIncrement)
    def _getSpiralIndex(self, lon, k, approx=round):
        return approx((lon)/(CIRCLE*phi**-k))
    def getSphericalIndex(self, spherical):
        return self.getCartesianIndex(toCartesian(spherical))
    def getCartesianIndex(self, cartesian):
        spherical = toSpherical(self.frame.world_to_frame(cartesian))
        return int(self.mapping.array[self.mapping.posToId(spherical)])
    def _getIndex(self, (lat, lon)):
        '''Returns the approximate index of the coordinates given.
        The position of the index appears to always be at least 
        a neighbor to the correct one.
        Operates in O(log(N)) time where N is the 
        total number of points on the sphere.
        This method was developed independant of Swinbank & Purser (2006)
        and lacks theoretical grounding. 
        To compensate, documentation here will be generous.
        BLACK MAGIC BEGINS HERE'''
        
        #find the closest index in terms of latitude 
        z = sin(lat)
        index = self._getZoneIndex(z, round)
        
        #find the "zone" based on latitude as described by Swinbank & Purser (2006).
        #Nearest neighbors within each zone are 
        #connected by a spiral whose slope is unique to that zone
        zone = self._getZone(lat)
        
        #correct index is guaranteed to be within fib(zone+1)
        #we now traverse this remaining search space in O(log) time
        #this is done with an algorithm that converts 
        #the fraction of longitude offset to base-phi or "phinary"
        remainder = getLonDistance(self._getLon(index), lon)/CIRCLE
        for k in xrange(1, abs(zone+1)):
            remaindertemp = (remainder*phi)
            remainder = remaindertemp % 1.0
            if abs(remaindertemp) > 1.0:
                index+=(-1)**k*fib(k)
        index = int(bound(index, -self.pointNum+1, self.pointNum))
        return index
    
    #---GET COORDINATE FUNCTIONS
    def _getZ(self, index):
        return bound(index * self.zIncrement, -1.0, 1.0)
    def _getLon(self, index):
        return (index*CIRCLE/(phi))%CIRCLE
    def _getSpherical(self, index):
        index = min(index, self.pointNum) if index > 0 else \
                max(index, -self.pointNum)
        return (asin(self._getZ(index)), self._getLon(index))
    def getSpherical(self, index):
        return toSpherical(self.getCartesian(index))
    def getCartesian(self, index):
        return self.frame.frame_to_world(self.points[index])
        
    
    #---COLLECTION METHODS
    def add(self, point):
        self.coverage[point.id] = point
    def remove(self, point):
        self.coverage[point.id] = None
    
    #---PROXIMITY METHODS
    def getIndices(self):
        return xrange(-self.pointNum,self.pointNum+1)
    
    def _getCellNeighborId(self, index, sign, zone):
        return bound(index + sign*fib(zone), -self.pointNum, self.pointNum)
    def getCellNeighborIds(self, index, zones=[-1, 0, 1]):
        '''Returns indices of cells neighboring the one specified by the given index.
        This is a frequently used function that is highly optimized.'''
        zone = self._getZone(asin(self._getZ(index)))
        yield self._getCellNeighborId(index, -1, zone-1)
        yield self._getCellNeighborId(index, -1, zone)
        yield self._getCellNeighborId(index, -1, zone+1)
        yield self._getCellNeighborId(index,  1, zone-1)
        yield self._getCellNeighborId(index,  1, zone)
        yield self._getCellNeighborId(index,  1, zone+1)
    def _getCellNeighbors(self, index):
        '''Returns points occupying cells neighboring the cell specified by index'''
        neighborIndices = self.getCellNeighborIds(index)
        return [self.coverage[neighborIndex] 
                for neighborIndex in neighborIndices 
                if self.coverage[neighborIndex]]
    def getNeighbors(self, points, getIsNeighbors = lambda point1, point2: True):
        if type(points) != list: 
            points = [points] 
        for point in points:
            for i in self.getNeighborIds(point):
                neighbor = self.coverage[i]
                if neighbor and getIsNeighbors(point, neighbor):
                    yield neighbor
    def getNeighborIds(self, *points):
        '''Returns indices of cells neighboring the given points.
        No indices are duplicated'''
        for point in points:
            for i in self.getCellNeighborIds(point.id):
                yield i
    def getNearest(self, point, id=None, points=[]):
        if not points: 
            if not id: id = self.getCartesianIndex(point)
            points = self._getCellNeighbors(id)
        if points:
            return min(points, key=lambda other: other.getDistance(point)) 
        else:
            return None
    def getCollision(self, cartesian, approx=False):
        id = self.getCartesianIndex(cartesian)
        overlapping = self.coverage[id]
        if overlapping:
            return overlapping
        elif not approx:
            nearest = self.getNearest(cartesian, id)
            if  nearest:
                return nearest
            
        
        
        