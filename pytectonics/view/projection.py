from visual import sphere, convex, vector
from math import sin, cos
from itertools import product
from pytectonics.utils import *
from pytectonics.control import PanControl, SpinControl

class GlobeProjection: 
    def __init__(self, rpm=1./5):
        self.layerBase = list(product([0.5,0,-0.5], repeat=3))
        self.control = SpinControl(rpm)
    def getBackground(self, **background):
        return sphere(**background)
    def getForeground(self, world, view):
        renderable=[rock for rock in world 
                    if view.getRenderable(rock)]
        return [layer.render(renderable, self, view) 
                for layer in view.layers]
    def getPos(self, rock, heightMod=0):
        return rock.cartesian * (1.+heightMod)
    
class MapProjection: 
    def __init__(self):
        self.layerBase = []
        self.control = PanControl()
        self._view = None
        for i in xrange(16):
            self.layerBase.append((pi/2*sin(16.*i/pi), 
                                   pi/2*cos(16.*i/pi),
                                   -0.1))
    def getBackground(self, **background):
        return convex(pos=list(product([-SEMICIRCLE,SEMICIRCLE], 
                                       [-RIGHT_ANGLE,RIGHT_ANGLE], 
                                       [-0.1,0])), 
                      **background)
    def getForeground(self, world, style):
        updated = []
        
        for plate in world.plates:
            renderable=[rock for rock in plate.samples
                        if style.getRenderable(rock)]
            for layer in style:
                renderable2 = [rock for rock in renderable
                               if layer.getContains(rock) and 
                               any([not layer.getContains(neighbor) 
                                    for neighbor in plate.samples.getNeighbors(rock)])]
                groups = plate.getGroups(renderable2, 
                             getIsNeighbors = lambda rock1, rock2: 
                                (self.getPos(rock1) - self.getPos(rock2)).mag < world.avgDistance)
                for group in groups:
                    updated.append(layer.render(group, self, style))
                    
        return updated
    
    def getPos(self, rock, heightMod=0):
        lat, lon = rock
        return vector(lon%(2*pi)-pi, lat, heightMod)