from visual import convex

class Layer:
    def __init__(self, color, shape=convex, layerNum=0., getContains=lambda rock: True):
        self.shape = shape
        self.color = color
        self.getContains = getContains
    def render(self, rocks, projection, style):
        heightMod = style.getHeightMod(self)
        return self.shape(pos = [projection.getPos(rock, heightMod) 
                             for rock in rocks
                             if self.getContains(rock)] + projection.layerBase,
                           color = self.color,
                           **style.layerStyle)