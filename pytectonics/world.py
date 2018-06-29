from pytectonics import Plate, Crust, GeoCoordinate, Hotspot, FibGrid
from pytectonics.utils import *
from math import sqrt, pi, asin
import random


class World:
    #lengths in m, density in kg/m^3
    
    mantleDensity=3300
    waterDensity=1026  
    oceanCrustDensity=2890 #Carlson & Raskin 1984
    continentCrustDensity=2700
    #height of sea level relative to displacement from the mantle (meters)
    #determined empirically
    
    
    def __init__(self, radius, resolution, plateNum, 
                 hotspotNum, hotspotHeat, 
                 continentNum, continentSize,
                 maxMountainWidth=300, Grid=FibGrid):
        self.age = 0
        
        self.radius = radius
        avgPointDistance = 2*pi/resolution
        
        template = Grid(avgPointDistance)
        self.plates = [Plate(GeoCoordinate(self.randomPoint()), self,
                             Grid(avgPointDistance, mapping=template.mapping), 
                             random.gauss(42.8, 27.7), toCartesian(self.randomPoint()))
                       for i in xrange(plateNum)]
        self.hotspots = [Hotspot(self.randomPoint(), 
                                 random.randint(hotspotHeat),
                                 self, 2)
                         for i in xrange(hotspotNum)]
        shields = [GeoCoordinate(self.randomPoint())
                   for i in xrange(continentNum)]
        continentSize = self.distanceToRadians(continentSize)

        for i in template.getIndices():
            cartesian = template.getCartesian(i)
            nearestPlate = template.getNearest(cartesian, points=self.plates)
            isContinent = any([shield.getDistance(cartesian) < continentSize
                                    for shield in shields])
            Crust(nearestPlate, self, isContinent, id=i)
        
        self.seaLevel = 3790 
        self.maxMountainWidth = maxMountainWidth
        self.avgDistance = avgPointDistance
        area = 4*pi / template.totalPointNum
        d = sqrt(area / sqrt(5))
        self.minDistance = sqrt(2)*d
    def randomPoint(self): 
        '''Returns random point on a globe in terms of distances.
        evenly distributes points, correctly considering curvature of globe '''
        return     (asin(2 * random.random() - 1), 
                    2*pi*random.random()) 
    def distanceToRadians(self, distance):
        return float(distance) / self.radius
    def radiansToDistance(self, radians):
        return radians * self.radius
    def __iter__(self):
        for plate in self.plates:
            for crust in plate.grid:
                yield crust
    def dock(self):
        for plate in self.plates: plate.dock()
    def move(self, timestep):
        for plate in self.plates: plate.move(timestep)
    def collide(self):
        for plate in self.plates:
            plate.collide()
    def rift(self):
        for plate in self.plates:
            plate.rift()
    def isostacy(self):
        for crust in self:
            crust.isostacy()
    def tryErupt(self, timestep):
        for hotspot in self.hotspots:
            hotspot.tryErupt()
    def clean(self):
        for plate in self.plates:
            if not any([crust for crust in plate.grid 
                        if not crust.isContinent() 
                        and not crust.subductedBy]):
                plate.destroy()
                for other in plate.getNeighborPlates():
                    other.clean()
                
    def update(self, timestep):
        self.move(timestep)
        self.isostacy()
        self.collide()
        self.dock()
        self.rift()
        self.clean()
        #self.tryErupt(timestep)
        self.age += timestep
