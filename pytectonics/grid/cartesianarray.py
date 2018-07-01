import numpy
from pytectonics.utils import SEMICIRCLE, RIGHT_ANGLE, CIRCLE, bound

class CartesianArray:
    """Not to be confused with a *Grid class.
    Wrapper for a numpy array storing integers mapped over a globe.
    Allows easy conversion from lat/lon coordinate to grid cell."""
    def __init__(self, *shape):
        assert len(shape)>=2
        self.numLat = int(shape[0]) 
        self.numLon = int(shape[1])
        self.array = numpy.zeros([int(x) for x in shape])
    def idToPos(self, coord):
        i,j = coord
        return float(i)/self.numLat * SEMICIRCLE - RIGHT_ANGLE, \
               float(j)/self.numLon * CIRCLE
    def posToId(self, coord):
        lat, lon = coord
        lon = lon + CIRCLE if lon < 0 else lon 
        i = round((lat + RIGHT_ANGLE)/SEMICIRCLE * self.numLat)
        i = bound(i, 0, self.numLat-1)
        j = round(lon/CIRCLE * self.numLon)
        j = bound(j, 0, self.numLon-1)
        return i,j
    def getIds(self):
        for i in range(self.numLat):
            for j in range(self.numLon):
                yield i,j
    def getCell(self, coord):
        lat,lon = coord
        i,j = self.posToMappingId((lat, lon))
        return int(self.mapping[i,j])
