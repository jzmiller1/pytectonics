from visual import label, scene
from visual.controls import *

class View:
    '''View abstraction of the Model View Control architecture.
    Represents a combination of projection (e.g. globe, cassini, equarectangular) 
    and style (e.g. satellite, topography, etc.).
    Manages changes made to projection and style that are specific to the graphics library.'''
    def __init__(self, world, projection, style):
        
        scene.title = 'pyTectonics'    
        
        self._world = world
        self._projection=projection
        self._style = style
        
        self._foreground=[]
        self._background=None
        
        self._updateBackground()
        self._projection.control.start()
        
        def getPos(row, col, rowTop=75, rowHeight=25, colWidth=50):
            return (col*colWidth,
                    rowTop - row*rowHeight)
            
        self.control = controls()
        self.speedSlider = slider(pos = getPos(0, -1.5),      
                                  length = getPos(0, 3)[0],   
                                  min=0., max=10., value=1.)
        self.ageLabel =   label(display=self.control.display, text='Initializing...', 
                                pos = getPos(.5,1),
                                opacity=0, line=False, box=False)
        self.speedLabel = label(display=self.control.display, text='Speed: 1 My', 
                                pos = getPos(.5,-1),
                                opacity=0, line=False, box=False)
        
        self.viewMenu = menu(pos=getPos(2, -1), width=60, height=20, text='Map type')
        
        self.projectionMenu = menu(pos=getPos(2, 1), width=60, height=20, text='Projection')
        
        
    def setProjection(self, projection):
        if projection != self._projection:
            if self._projection:
                self._projection.control.stop.set()
                
            self._projection = projection
            self._projection.control.start()
            self._updateBackground()
            for rendered in self._foreground: rendered.visible = False
            
    def setStyle(self, style):
        if style != self._style:
            self._style = style
            self._updateBackground()
            for rendered in self._foreground: rendered.visible = False
    def _formatTime(self, my):
        if my >= 1000:
            return str(round(my)/1000) + ' By'
        else:
            return str(round(my)) + ' My'
        
    def updateSpeed(self):
        self.speedLabel.text = 'Speed: ' + self._formatTime(self.speedSlider.value)
        
    def _updateBackground(self):
        if self._background:
            self._background.visible = False
        self._background = self._projection.getBackground(**self._style.backgroundStyle)
        
    def update(self):
        updated = self._projection.getForeground(self._world, self._style)
        for rendered in self._foreground: rendered.visible = False
        self._foreground = updated
        
        self.ageLabel.text = 'Age: '+self._formatTime(self._world.age)
        self.updateSpeed()
    
    