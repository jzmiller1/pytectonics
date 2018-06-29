"""
Common mathematical constants and functions
"""

from math import pi, sqrt, copysign, cos, sin, asin, atan2
from visual import vector, cross, mag


#mathmatical constants
RIGHT_ANGLE = pi / 2
SEMICIRCLE = pi
CIRCLE = pi * 2
phi = 1.61803398874989484820
sqrt5 = sqrt(5) 
#So why is sqrt(5) a constant? 
#1.) It has an intrinsic relation to phi in 
#    what makes it very similar to other mathematical constants
#2.) It produces tangible gains in efficiency 

SEC_IN_MIN = 60.
 
#supportive math function not implemented in the math library
def fib(n): 
    '''Returns an approximation of the nth fibonacci number'''
    return int(round(phi**n/sqrt5))
def sign(n):
    """Returns 1 for positive, -1 for negative, and 0 for 0"""
    return copysign(1,n)
def getLonDistance(angle1, angle2):
    '''Returns angular distance of two angles'''
    return (angle1-angle2+ CIRCLE) % CIRCLE
def bound(x, floor, ceil):
    return max(min(x, ceil),floor)


def toCartesian(spherical):
    '''Converts lat lon coordinates to cartesian'''
    lat, lon=spherical
    return vector(cos(lat)*cos(lon), 
                  sin(lat), 
                  -cos(lat)*sin(lon))
def toSpherical(cartesian):
    return asin(cartesian.y), atan2(-cartesian.z, cartesian.x)
def moment(point, end1, end2=vector(0,0,0)):
    '''Returns the moment defined as the distance between a point 
    and a line formed by two endpoints, end1 and end2.
    All points must be given as 3d vectors'''
    return mag(cross(point - end2, point - end1)) /     \
           mag(end1 - end2)
           