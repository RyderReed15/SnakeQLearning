import pygame

class Button(object):
    
    button = None
    
    def __init__(self, x, y, width, length, text, textObject, color, function):
        self.button = pygame.Rect(x, y, width, length)
        self.text = textObject.render(text, True, color)
        self.textSize = textObject.size(text)
        self.pos = (x,y)
        self.width = width
        self.length = length
        self.function = function
        self.textPos = ((x+(width - self.textSize[0])/2), (y+(length - self.textSize[1])/2))
        width
        
    def getBounds(self):
     
        return (self.pos[0], self.pos[1], self.pos[0]+self.width, self.pos[1]+self.length)
        
    def getText(self):
     
        return self.text
    
    def getTextPos(self):
     
        return self.textPos
        
    def getRect(self):
     
        return self.button
        
    def getFuntion(self):
     
        return self.function