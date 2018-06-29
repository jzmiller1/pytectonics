import threading
import Queue
from visual import scene, rotate, rate
from pytectonics.utils import *
import time

class SpinControl(threading.Thread):
    def __init__(self, rpm=0., fps=30.):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.rpm = rpm
        self.fps = fps
    def run(self):
        scene.userspin = True
        scene.autoscale = True
        scene.center = 0,0,0
        
        dragging = False
        
        lastTime = time.clock()
        elapsedTime = 0.
        
        while not self.stop.isSet():
            rate(self.fps)
            
            newTime = time.clock()
            elapsedTime = newTime - lastTime
            lastTime = newTime
            
            if scene.mouse.events: 
                mouse = scene.mouse.getevent()
                if mouse.press:
                    dragging = True
                elif mouse.release:
                    dragging = False
                    
            if not dragging and self.rpm:
                increment = CIRCLE * self.rpm / SEC_IN_MIN * elapsedTime
                scene.forward = rotate(scene.forward, increment, axis=(0.,-1.,0.))
                
        #reinitialize the thread so that it may be called again
        threading.Thread.__init__(self)