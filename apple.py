import pygame

class Apple(object):
    
    def __init__(self, pos, pps):
        self.apple = pygame.Rect(pos[0]*pps, pos[1]*pps, pps, pps)

        return
        
    def getRect(self):
        
        return self.apple
    
    pass