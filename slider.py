import pygame

class Slider(object):
    
    
    def __init__(self, x, y, length, width, variable, startPos, text, textObject):
        self.variable = variable
        self.pos = (x,y)
        self.size = (length, width)
        self.textObj = textObject
        self.circlePos = (x+startPos[0],y+startPos[1])
        self.checks = (x+length/3, x+length*(2/3), x+length)
        self.string = text
        self.text = textObject.render(text, True, (255,255,255))
        self.moveable = False
        return
        
    def getChecks(self):
        return self.checks
    
    def getPos(self):
        
        return self.pos
    
    def getEnd(self):
        
        return (self.pos[0]+self.size[0], self.pos[1]+self.size[1]+20)
        
    def getText(self):
        
        return self.text
        
    def setText(self, string):
        self.text = self.textObj.render(string, True, (255,255,255))
        return 
        
    def getString(self):
        
        return self.string   
   
    def getSize(self):
        
        return self.size
            
    def getMoveable(self):
        return self.moveable
    
    def setMoveable(self, moveable):
        self.moveable = moveable
        return 
        
    def getCirclePos(self):
        
        return self.circlePos
        
    def setPos(self, x):
        self.circlePos = (x, self.circlePos[1])
        return 
            
    def getVariable(self):
        
        return self.variable