'''  A program to simulate tectonics.
 
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
'''

from pytectonics import *
import cProfile

#initialize world
world = World(radius=6367, resolution=360/5, 
              plateNum=7, 
              hotspotNum=0, hotspotHeat=0, 
              continentNum=3, continentSize=1250,
              Grid=FibGrid)
    
#initialize GUI
#initialize render window
view = View(world, projection=GlobeProjection(), style=debugStyle)

#view.speedLabel.action = lambda: view.updateSpeed()

view.viewMenu.items.append(('Satellite', lambda: view.setStyle(satelliteStyle))) 
view.viewMenu.items.append(('Relief',    lambda: view.setStyle(reliefStyle))) 
view.viewMenu.items.append(('Thickness', lambda: view.setStyle(thicknessStyle))) 
view.viewMenu.items.append(('Debug',     lambda: view.setStyle(debugStyle)))

view.projectionMenu.items.append(('Map',  lambda: view.setProjection(MapProjection())))
view.projectionMenu.items.append(('Globe',lambda: view.setProjection(GlobeProjection())))

def main():
    while True:
        view.update()
        timestep = (view.speedSlider.value)
        if timestep:
            world.update(timestep)
def benchmark():
    for i in xrange(50):
        view.update()
        world.update(1.0)
        
        
main()
#cProfile.run('benchmark()')