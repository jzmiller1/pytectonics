from math import *
from pytectonics.utils import *

class GeoCoordinate:
    _idCounter = 0
    def __init__(self, spherical=None, id=None, cartesian=None):
        self._spherical = spherical
        self._cartesian = cartesian
        self.id = id
        GeoCoordinate._idCounter += 1
    def __getitem__(self, key):
        return self._getSpherical()[key]
    def __dict__(self):
        return self.id
    
    def _getSpherical(self):
        if not self._spherical: 
            self._spherical = toSpherical(self._cartesian)
        return self._spherical
    def _setSpherical(self, spherical):
        self._spherical = spherical
        self._cartesian = None
    spherical = property(_getSpherical, _setSpherical)
    
    def _getCartesian(self):
        if not self._cartesian: 
            self._cartesian = toCartesian(self._spherical)
        return self._cartesian
    def _setCartesian(self, cartesian):
        self._cartesian = cartesian
        self._spherical = None
    cartesian = property(_getCartesian, _setCartesian)
    
    def getArcDistance(self, other):
        '''Returns distance between two points on a globe given in terms of distance.
        Correctly considers the curvature of the globe.'''
        lat1, lon1 = self
        lat2, lon2 = other
        latChange = abs(lat1-lat2)
        lonChange = abs(lon1-lon2)
        return 2 * asin(sqrt(sin(latChange/2) ** 2 + \
                             cos(lat1) * cos(lat2) * sin(lonChange/2) ** 2))
    def getDistance(self, other):
        '''Returns distance between two points '''
        return (self.cartesian - other).mag
    def rotate(self, angularSpeed, eulerPole, inPlace=True):
        rotated = self.cartesian.rotate(angularSpeed, 
                                         axis=eulerPole.astuple())
        if inPlace:
            self.cartesian = rotated
        else:
            return GeoCoordinate(spherical=None,
                                 cartesian=rotated,
                                 id=self.id)
            