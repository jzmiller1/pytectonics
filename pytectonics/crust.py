from pytectonics.utils import *
from pytectonics import GeoCoordinate
from visual import vector

class Crust(GeoCoordinate):
    def __init__(self, plate, world, isContinent=False, id=None):
        self.world=world
        self._plate = plate
        self._id = id
        self._cartesian = plate.grid.points[id]
        
        self.subductedBy = None
        self.subducts    = None
        self._firstSubductedBy = None
        
        self._isContinent=isContinent
        if isContinent:
            thickness=36900 #+/- 2900, estimate for shields, Zandt & Ammon 1995
            density=world.continentCrustDensity + plate.densityOffset
        else:
            thickness=7100 #+/- 800, White McKenzie and O'nions 1992
            density=world.oceanCrustDensity + plate.densityOffset
        self.density = density
        self._thickness = thickness
        
        rootDepth = self._thickness * self.density / self.world.mantleDensity
        self.displacement = self._thickness - rootDepth
        
        plate.add(self)
        
    def _getPlate(self):
        return self._plate
    def _setPlate(self, plate):
        self._plate = plate
    plate = property(_getPlate, _setPlate)
    
    def _getId(self):
        return self._id
    def _setId(self, id):
        self._id = id
        self._cartesian = self.plate.grid.points[id]
    id = property(_getId, _setId)
    
    def _getSpherical(self):
        return toSpherical(self.cartesian)
    spherical = property(_getSpherical)
    
    def _getCartesian(self):
        return self.plate.grid.frame.frame_to_world(self._cartesian)
    cartesian = property(_getCartesian)
    
    def isContinent(self):
        return self.thickness > 17000
    
    def isDetaching(self):
        '''Returns whether subducting crust should be detaching from overriding crust
        Detachment occurs after travelling a given distance under 
        a subducting crust. This effectively determines the size 
        of mountain ranges and position of volcanic arcs 
        relative to plate boundaries.
        A mountain width was chosen over the angle of subduction because:
        * it is simpler
        * maxMountainWidth is far more user friendly than subductionAngle
        * there is no known model for subduction angles that does not 
          introduce even more user un-friendly parameters
        '''
        if not self._firstSubductedBy:
            return False
        else:
            distanceSubductedAngular = self.getArcDistance(self._firstSubductedBy)
            distanceSubducted = self.world.radiansToDistance(distanceSubductedAngular)
            return distanceSubducted > self.world.maxMountainWidth
    
    def _getPressure(self):
        pressure = self._thickness*self.density
        if self.subducts:
            pressure += self.subducts._thickness*self.subducts.density
        #include water
        #if self.elevation < 0 and not self.subductedBy:
        #    pressure += -self.elevation * self.world.waterDensity
        return pressure
    pressure = property(_getPressure)
    
    def _getSmallCircleRadius(self):
        return moment(self.cartesian, self.plate.eulerPole)
    smallCircleRadius = property(_getSmallCircleRadius)
    
    def _getInertialMoment(self):
        '''Returns angular mass/moment of inertia'''
        #first, get the moment defined by self.cartesian and axis of rotation
        return self.pressure * self.smallCircleRadius ** 2
    inertialMoment = property(_getInertialMoment)
    
    def _getDensity(self):
        return self.pressure / self.thickness
    density = property(_getDensity)
    
    def _getElevation(self):
        return self.displacement - self.world.seaLevel
    elevation = property(_getElevation)
    
    def _getThickness(self):
        thickness = self._thickness
        #include water
        if self.subducts:
            thickness += self.subducts._thickness
        #if self.elevation < 0 and not self.subductedBy:
        #    thickness += -self.elevation
        return thickness
    thickness = property(_getThickness)
    
    def isostacy(self):
        '''Calculates elevation as a function of crust density.
        This was chosen over an empirical model in earlier code
        as it only requires knowledge of crust density and thickness, 
        which are relatively well known.
        '''
        thickness = self.thickness
        rootDepth = thickness * self.density / self.world.mantleDensity
        displacement = thickness - rootDepth 
        #if self.elevation < 0: displacement + self.elevation
        
        
        #calculates eustacy of oceans
        #if self.elevation < 0:
        #    displacedWater = min(displacement, self.world.seaLevel) - self.displacement 
        #    self.world.seaLevel += displacedWater / self.world.grid.totalPointNum
        self.displacement = displacement 
        
    def erupt(self):
        '''Attempts to erupt a volcano on the surface of crust.
        Height calculation based upon model by Ben-Avraham & Nur (1980),
        which was chosen due to its simplicity.
        The following assumptions apply:
        * Density of melted crust is equivalent to that of continental crust.
          Observed densities seem close to this assumption,
          and the assumption assures continental crust does not become
          more dense over time.
        * Melt source for volcano always occurs where subducted crust 
          detaches from subducting crust, i.e. at a depth defined by the 
          subducting crust's thickness.
        '''
        meltDensity = self.world.continentCrustDensity
        rockDensity = self.world.oceanCrustDensity
        thickness = self.thickness
        if self.elevation < 0:
            thickness -= ((meltDensity-self.world.waterDensity)/(self.density-meltDensity)) * \
                          abs(self.elevation)
            height = thickness * ((self.density - meltDensity) 
                                  / meltDensity)
            heightChange = height + abs(self.elevation)
        else:
            heightChange = thickness * ((self.density - meltDensity) 
                                        / meltDensity)
        pressure = (thickness*self.density) + \
                   (heightChange*self.density)
        density  = pressure / (thickness + heightChange)
        
        self._thickness += heightChange
        self.density = density
    def collide(self, other, densityThreshold=.1):
        if self.subductedBy:
            top, bottom = other, self
        elif other.subductedBy:
            top, bottom = self, other
        else:
            #otherwise, lightest crust goes on top
            top, bottom = sorted([self, other], 
                                      key=lambda crust: crust.density)
        
        #TODO: subducted continental plates should not subduct ocean
        if top.subducts != bottom or bottom.subductedBy != top:
            '''destroy the crust upon detachment from overriding plate''' 
            if bottom.isDetaching():
                if bottom.isContinent() and top.isContinent():
                    bottom.plate.requestDock(top, bottom)
                else:
                    #erupt volcano, where none has occurred before
                    top.erupt()
                    #destroy crust
                    bottom.destroy()
                    top.plate.update(top)
            else:
                if not bottom._firstSubductedBy:
                    bottom._firstSubductedBy = top
                
                top.subducts    = bottom
                bottom.subductedBy = top
                
                bottom.plate.update(bottom)
                top.plate.update(top)
    
    def copy(self, plate, id):
        copied = Crust(plate, plate.world, isContinent=self.isContinent(), id=id)
        copied._thickness = self._thickness
        copied.density = self.density
        copied.subductedBy = self.subductedBy
        copied.subducts = self.subducts
        return copied
    
    def destroy(self):
        self.plate.remove(self)
        if self.subductedBy:
            self.subductedBy.subducts = None
        if self.subducts:
            self.subducts.subductedBy = None