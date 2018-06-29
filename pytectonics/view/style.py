from visual import vector, points, convex
from math import pi
from pytectonics.view import Layer

class Style:
    '''Represents a series of layers, layer styles, and background'''
    def __init__(self,
                 layers = {}, 
                 layerWidth=0.001, 
                 layerStyle={},
                 backgroundStyle={},
                 getRenderable=lambda rock: True):
        
        self.layers = layers
        self.layerWidth = layerWidth
        self.layerStyle = layerStyle
        
        self.backgroundStyle = backgroundStyle
        self.getRenderable = getRenderable
    def __iter__(self):
        return self.layers.__iter__()
    def getHeightMod(self, layer):
        return (self.layers.index(layer) + 1) * self.layerWidth
        
def elevationFunc(elevation):
    return lambda rock: rock.elevation > elevation
def thicknessFunc(thickness):
    return lambda rock: rock.thickness > thickness
        
debugStyle     = Style(backgroundStyle = {'opacity': 0.75},
                       layerStyle = {'size': 5},
                       layers=[Layer(color=vector(.0,.0,.4),             shape=points),                       
                               Layer(color=vector(80.,110.,30.)/255.*1.5,shape=points,
                                     getContains=elevationFunc(0)),
                               Layer(color=vector(.4,.4,.4),             shape=points,
                                     getContains=elevationFunc(5000)),
                               Layer(color=vector(1.,1.,.0),             shape=points,
                                     getContains=elevationFunc(15000)),
                               Layer(color=vector(1.,.0,.0),             shape=points,
                                     getContains=lambda rock: rock.subductedBy)]
                       )

reliefStyle    = Style(backgroundStyle = {'color': vector(.0,.0,.2)},#Deep water
                       getRenderable=lambda rock:  
                            rock.elevation > -2000 and not rock.subductedBy,
                       layers=[Layer(color=vector(.0,.0,.4), getContains=elevationFunc(-2000)),
                               Layer(color=vector(.0,.2,.4), getContains=elevationFunc(-1000)),  
                               Layer(color=vector(.0,.2,.0), getContains=elevationFunc(0)),
                               Layer(color=vector(.0,.4,.0), getContains=elevationFunc(1000)),
                               Layer(color=vector(.2,.4,.0), getContains=elevationFunc(2000)),
                               Layer(color=vector(.4,.4,.0), getContains=elevationFunc(3000)),
                               Layer(color=vector(.4,.4,.2), getContains=elevationFunc(4000)),
                               Layer(color=vector(.4,.4,.4), getContains=elevationFunc(5000)),
                               Layer(color=vector(.6,.6,.6), getContains=elevationFunc(6000)),
                               Layer(color=vector(.8,.8,.8), getContains=elevationFunc(7000)),
                               Layer(color=vector(.8,.8,1.), getContains=elevationFunc(8000)),
                               Layer(color=vector(1.,1.,1.), getContains=elevationFunc(9000))]
                       )                   

def _getThicknessColor(thickness):
    return vector(3.0,2.0,1.0) * thickness / 1e5
thicknessStyle = Style(backgroundStyle = {'color': _getThicknessColor(7e3)},#Deep water
                       getRenderable=lambda rock:  
                            rock.thickness > 10000 and not rock.subductedBy,
                       layers=[Layer(color=_getThicknessColor(float(thickness)),
                                     getContains=thicknessFunc(thickness))
                               for thickness in xrange(10000, 60000, 5000)]
                       )
satelliteStyle = Style(backgroundStyle = {'color': vector(10.,10.,50.)/255.*1.},
                       getRenderable=lambda rock: 
                            rock.elevation > -200 and not rock.subductedBy,
                       layers=[Layer(color=vector(10.,150.,140.)/255.,   #Shallow water
                                     getContains=elevationFunc(-200)),  
                               Layer(color=vector(80.,110.,30.)/255.*1., #Land
                                     getContains=elevationFunc(0)),
                               Layer(color=vector(250.,250.,250.)/255.,  #Glacier
                                     getContains=lambda rock: 
                                         rock.elevation > 0 and
                                         abs(rock[0]) > (7./9.) * (pi/2.)
                                     ),
                               Layer(color=vector(140.,140.,140.)/255.,  #Mountain
                                     getContains=elevationFunc(5000))]
                       )
