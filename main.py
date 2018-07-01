"""  A program to simulate tectonics.
 
  Basis for code was provided by Mark Isaak, Copyright 1988
  You may distribute this however you like, as long as you don't sell it
  and you keep this notice in it.
 
  Wish list:
   x Do it on a sphere, not a square torus
   x Give plates angular momentum
     Make some constants variable
     Horsts and grabens
   x Let 2 plates fuse together 
     Let 1 plate split apart sometimes
     Astroblemes
   x Take density of rock into account
"""

from pytectonics.world import World
from pytectonics.utils import toSpherical
from pytectonics.grid.fibgrid import FibGrid
import cProfile

# initialize world
world = World(radius=6367, resolution=360/5, 
              plateNum=7, 
              hotspotNum=0, hotspotHeat=0, 
              continentNum=3, continentSize=1250,
              Grid=FibGrid)


def main():
    while True:
        timestep = 1.0
        if timestep:
            world.update(timestep)
            plate = world.plates[0]
            print("STEP")
            print([toSpherical(point) for point in plate.grid.points[0:3]])
            print(plate._cartesian)
            print(plate._spherical)


def benchmark():
    for i in range(50):
        world.update(1.0)
        
        
main()
#cProfile.run('benchmark()')