import threading
import Queue
from visual import scene, rate
from pytectonics.utils import *

class PanControl(threading.Thread):
    def __init__(self, fps=30.):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.fps = fps
    def run(self):
        pos = None
        scene.forward = (0.,0.,-1.)
        scene.userspin = False
        scene.autoscale = False
        while not self.stop.isSet():
            rate(self.fps)
            
            if scene.mouse.events: 
                mouse = scene.mouse.getevent()
                if mouse.drag:
                    pos = mouse.pos
                    scene.cursor.visible = False
                elif mouse.release:
                    scene.cursor.visible = True
                    pos = None
            if pos:
                new = scene.mouse.pos
                if new!=pos:
                    center = scene.center + mouse.pos - new
                    center.x = bound(center.x, -SEMICIRCLE, SEMICIRCLE)
                    center.y = bound(center.y, -RIGHT_ANGLE,RIGHT_ANGLE)
                    scene.center = center
                    pos = new 
                    
        #reinitialize the thread so that it may be called again
        threading.Thread.__init__(self)