from pytectonics import GeoCoordinate

class Hotspot(GeoCoordinate):
    def __init__(self, spherical, world, frequency):
        self.spherical = spherical
        self.id = world.grid.getIndex(self)
        self.world = world
        self.frequency=frequency #frequency of volcano formation, per million years
    def tryErupt(self, timestep):
        rock=self.world.grid.getNeighbor(self)
        #locate nearest rock
        for i in self.frequency * timestep:
            rock.erupt()
        