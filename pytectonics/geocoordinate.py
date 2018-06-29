from math import sqrt, cos, sin, asin
from pytectonics.utils import toSpherical, toCartesian
from numpy import asarray, sqrt, dot, cos, sin, array

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
        if self._cartesian is None:
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
        x = self.cartesian - other
        return sqrt(x.dot(x))
    def rotate(self, angularSpeed, eulerPole, inPlace=True):
        def rotation_matrix(axis, theta):
            """
            Return the rotation matrix associated with counterclockwise rotation about
            the given axis by theta radians.

            From:
            https://stackoverflow.com/questions/6802577/rotation-of-3d-vector
            """
            axis = asarray(axis)
            axis = axis / sqrt(dot(axis, axis))
            a = cos(theta / 2.0)
            b, c, d = -axis * sin(theta / 2.0)
            aa, bb, cc, dd = a * a, b * b, c * c, d * d
            bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
            return array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                             [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                             [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

        axis = eulerPole
        theta = angularSpeed
        rotated = dot(rotation_matrix(axis, theta), self.cartesian)
        if inPlace:
            self.cartesian = rotated
        else:
            return GeoCoordinate(spherical=None,
                                 cartesian=rotated,
                                 id=self.id)
            