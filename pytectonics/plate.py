from math import pi, cos, asin
from pytectonics import GeoCoordinate, Crust
from pytectonics.utils import *
from visual import vector
import random
from collections import defaultdict

class Plate(GeoCoordinate):
    landElevation=800
    oceanElevation=-1000
    def __init__(self, spherical, world, grid, 
                 speed=0, eulerPole=toCartesian((pi/2,0))):
        '''speed is the absolute speed of a plate in km/Myr'''
        GeoCoordinate.__init__(self, spherical)
        self.world = world
        self.speed = speed 
        self.eulerPole = eulerPole
        self.grid = grid
        
        self._collidable = None
        self._riftable = None
        self._collisions = [None for i in xrange(0, self.grid.totalPointNum)]
        self._docking = set()
        
        #density offsets are needed so that crust of one plate always subducts
        #crust of another, provided they are both of the same type
        self.densityOffset = random.gauss(0, 40) #Carlson & Raskin 1984
    def __in__(self, crust):
        return crust in self.grid
    
    
    def _getVelocity(self):
        velocity = self.eulerPole
        velocity.mag = self.speed
        return velocity
    def _setVelocity(self, velocity):
        self.eulerPole = velocity.norm()
        self.speed = velocity.mag
    velocity = property(_getVelocity, _setVelocity)
    
    def _getCollidable(self):
        #TODO: there are a lot of related lazy loading properties here
        #might do with something initialized  
        if not self._collidable:
            self._collidable = set([crust for crust in self.grid 
                                 if any(self.getCollidableNeighborIds(crust))])
        return self._collidable.copy() #copy() invoked for use in loops
    collidable = property(_getCollidable)
    
    def _getRiftable(self):
        if not self._riftable:
            self._riftable = set()
            for crust in self.collidable:
                if not crust.subductedBy:
                    for id in self.getRiftableNeighborIds(crust):
                        self._riftable.add(id)
        return self._riftable.copy() #copy() invoked for use in loops
    riftable = property(_getRiftable)
    
    def add(self, crust):
        self.grid.add(crust)
        if self._collidable:
            for neighbor in self.grid.getNeighbors(crust):
                if any(self.getCollidableNeighborIds(neighbor)):
                    self._collidable.add(neighbor)
                elif neighbor in self._collidable:
                    self._collidable.remove(neighbor)
        if self._riftable:
            if not crust.subductedBy:
                for id in self.getRiftableNeighborIds(crust):
                    self._riftable.add(id)
                if crust.id in self._riftable:
                    self._riftable.remove(crust.id)
    def update(self, crust):
        '''Occurs upon subducting, becoming subducted, and refresh'''
        if self._collidable:
            self._collidable.add(crust)
            for neighbor in self.grid.getNeighbors(crust):
                self._collidable.add(neighbor)
        if self._riftable:
            if crust.subductedBy:
                for neighborId in self.getRiftableNeighborIds(crust):
                    if neighborId in self._riftable:
                        self._riftable.remove(neighborId)
                if crust.id in self._riftable:
                    self._riftable.remove(crust.id)
    def remove(self, crust):
        self.grid.remove(crust)
        if self._collidable:
            if crust in self._collidable:
                self._collidable.remove(crust)
        if self._riftable:
            for id in self.getRiftableNeighborIds(crust):
                if id in self._riftable:
                    self._riftable.remove(id)
            for neighbor in self.grid.getNeighbors(crust):
                if not neighbor.subductedBy:
                    for id in self.getRiftableNeighborIds(neighbor):
                        self._riftable.add(id)
                        
    
    def getCollidableNeighborIds(self, crusts):
        for neighborId in self.grid.getNeighborIds(crusts):
            if not self.grid[neighborId]:
                yield neighborId
            elif self.grid[neighborId].subductedBy:
                yield neighborId
    def getRiftableNeighborIds(self, crusts):
        for neighborId in self.grid.getNeighborIds(crusts):
            if not self.grid[neighborId]:
                yield neighborId
                
    def getGroups(self, crusts, getIsNeighbors=lambda crust1, crust2: True):
        '''Partitions a set of crusts into a list of groups 
        who share neighbors with one another'''
        unprocessed = list(crusts)
        while unprocessed:
            crust = unprocessed[0]
            unprocessed.remove(crust)
            group = [crust]
            neighbors = [crust]
            while neighbors:
                neighbors = [neighbor for neighbor in
                             self.grid.getNeighbors(neighbors, getIsNeighbors=getIsNeighbors)
                             if neighbor in unprocessed and neighbor not in group]
                group += neighbors
                for neighbor in neighbors:
                    if neighbor in unprocessed:
                        unprocessed.remove(neighbor)
            yield group
    def getGroup(self, crust, getIsNeighbors=lambda crust1, crust2: True):
        group = set([crust])
        neighbors = [crust]
        while neighbors:
            neighbors = [neighbor for neighbor in
                         self.grid.getNeighbors(neighbors, getIsNeighbors=getIsNeighbors)
                         if neighbor not in group]
            group |= set(neighbors)
        return group
    
    def getMass(self, crusts):
        '''Returns angular mass / moment of inertia'''
        return sum([crust.inertialMoment for crust in crusts])
    def getMomentum(self, crusts):
        '''Returns angular momentum'''
        return self.velocity * self.getMass(crusts)
    def getAngularSpeed(self, timestep=1):
        speed=self.speed * timestep
        smallCircleRadius = moment(self.cartesian, self.eulerPole) * self.world.radius
        return speed / smallCircleRadius
    def move(self, timestep):
        angularSpeed = self.getAngularSpeed(timestep)
        
        self.rotate(angularSpeed, self.eulerPole)
        self.grid.frame.rotate(angle=angularSpeed, 
                               axis=self.eulerPole.astuple())
    
    def isDockRequested(self, crust):
        return crust in self._docking
    #HACK: should be static, but calling as static causes circular dependency 
    #in package initialization
    def requestDock(self, top, bottom):
        if not top.plate.isDockRequested(bottom) and not bottom.plate.isDockRequested(top):
            #merging plates together
            bottomGroup = bottom.plate.getGroup(bottom, 
                                                lambda crust1, crust2: crust2.isContinent())
            topGroup    = top.plate.getGroup(top, 
                                             lambda crust1, crust2: crust2.isContinent())
            smaller, larger = sorted([bottomGroup, topGroup],
                                     key=lambda group: len(group))
            
            dockedTo = bottom.plate if bottom in larger else top.plate
            docking = bottom.plate if bottom in smaller else top.plate
            
            momentum = dockedTo.getMomentum(larger) + docking.getMomentum(smaller)
            mass     = dockedTo.getMass(larger)     + docking.getMass(smaller)
            self.velocity = momentum / mass
            
            for crust in smaller:
                dockedTo._docking.add(crust)
    def dock(self):
        for crust in self._docking:
            
            #TODO: subducted docking crust is added to thickness/density
            
            #remove from old plate
            crust.destroy()
            
            id = self.grid.getCartesianIndex(crust.cartesian)
            
            #getIndex does not always find nearest cell,
            #if crust already exists in cell, search neighbor cells by proximity
            if self.grid[id]:
                nearest = self.grid.getNearest(crust.cartesian, 
                    points=[GeoCoordinate(cartesian=self.grid.getCartesian(neighborId),
                                          id = neighborId) 
                            for neighborId in self.grid.getCellNeighborIds(id)])
                id = nearest.id
                
            #if cell is still occupied, search neighbors for those that aren't
            if self.grid[id]:
                empty = self.grid.getNearest(crust.cartesian, 
                    points=[GeoCoordinate(cartesian=self.grid.getCartesian(neighborId),
                                          id = neighborId) 
                            for neighborId in self.grid.getCellNeighborIds(id)
                            if not self.grid[neighborId]])
                id = empty.id
                
            #if all other efforts fails, replace existing crust
            if self.grid[id]:
                if self.grid[id] in self._docking:
                    print 'overwriting'
                self.grid[id].destroy()
            
            crust.copy(self, id)
            
        for plate in self.world.plates:
            plate._collidable = None
        self._docking=set()
        
    def trackCollisions(self, id, plate):
        self._collisions[id] = plate
        for neighborId in self.grid.getCellNeighborIds(id):
            self._collisions[neighborId] = plate
    def getCollisions(self, cartesian, plates, approx=False):
        '''Returns all collisions between cartesian and other plates'''
        for plate in plates:
            collision = plate.grid.getCollision(cartesian, approx=approx)
            if collision:
                yield collision
        yield None
    def getNeighborPlates(self):
        return [plate for plate in self.world.plates 
                      if plate!=self]
    def rift(self):
        #sort plates by distance to self for optimization purposes
        plates = sorted(self.getNeighborPlates(),
                        key = lambda plate: plate.getArcDistance(self))
        for id in self.riftable:
            #if I placed a crust here, would it collide with another plate?
            collidable = self._collisions[id] 
            collidable = [collidable] if collidable else plates
            
            cartesian = self.grid.getCartesian(id)
            collision = self.getCollisions(cartesian, collidable).next()
            if not collision:
                Crust(self, self.world, False, id)
                self._collisions[id] = None
            else:
                self.trackCollisions(id, collision.plate)
                collision.plate.trackCollisions(collision.id, self)
                    
    def collide(self):
        #sort plates by distance to self for optimization purposes
        plates = sorted(self.getNeighborPlates(),
                      key = lambda plate: plate.getArcDistance(self))
        for crust in self.collidable: 
            collidable = self._collisions[crust.id] 
            collidable = [collidable] if collidable else plates
            collision = self.getCollisions(crust.cartesian, 
                                           collidable, approx=True).next()
            if collision:
                self.trackCollisions(crust.id, collision.plate)
                collision.plate.trackCollisions(collision.id, self)
                crust.collide(collision)
            else:
                self._collisions[crust.id] = None
                if crust.subductedBy:
                    crust.subductedBy.subducts = None
                    crust.subductedBy = None
                    self._collidable.remove(crust)
                    
    def clean(self):
        self._collidable = None
        self._riftable   = None
        self._collisions =[None for i in xrange(0, self.grid.totalPointNum)]
        
    def destroy(self):
        self.world.plates.remove(self)
        for crust in self.grid:
            if crust.isContinent():
                nearestPlate = self.grid.getNearest(self.cartesian, 
                    points = self.getNeighborPlates())
                nearestPlate._docking.add(crust)
            else:
                if crust.subductedBy:
                    crust.subductedBy._thickness += crust._thickness
                crust.destroy()
    