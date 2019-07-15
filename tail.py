import pygame

class Tail(object):
    
    def __init__(self, pos, pps):
        self.tail = pygame.Rect(pos[0], pos[1], pps-1, pps-1)

        return
        
    def move(self, x, y):
        self.tail.move_ip(x, y)
        
        return
        
    def getRect(self):
        
        return self.tail
        
    def getPos(self):
        
        return (self.tail.left, self.tail.top)
    
    
    
    
