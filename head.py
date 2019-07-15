import pygame

from tail import Tail


class Head(object):
    body = []
    position = (0,0)
    coords = (0,0)
    data = []
    pps = 0
    oldPos = (0,0)
    
    def __init__(self, color, pos, pps):
        self.head = pygame.Rect(pos[0]*pps, pos[1]*pps, pps-1, pps-1)
        self.coords = pos
        self.body = []
        self.data = []
        for i in range(0,48):
            self.data.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        self.position = (pos[0]*pps, pos[1]*pps)
        self.oldPos = (pos[0]*pps, pos[1]*pps)
        self.pps = pps
        return
    
    
    
    def move(self, pos):
        cantMove = False
        self.data[int(self.coords[0])][int(self.coords[1])] = 0 
        if self.data[int(self.coords[0]+(pos[0]/self.pps))][int(self.coords[1]+(pos[1]/self.pps))] == 1:
            cantMove = True
        t = self.shiftTail(self.position)
        
        
        if not cantMove:
            self.coords = ((self.position[0]+pos[0])/self.pps, (self.position[1]+pos[1])/self.pps)
            self.head.move_ip(pos[0], pos[1])
        self.position = (self.head.left, self.head.top)


        return
        

    def shiftTail(self, pos):
        for i in range(len(self.body)-1,-1, -1):
            tail = self.body[i]
            nextTail = self.body[i-1]
            nextX = nextTail.getPos()[0]
            nextY = nextTail.getPos()[1]
            
            if (i == (len(self.body)-1)):
                    self.data[int(tail.getPos()[0]/self.pps)][int(tail.getPos()[1]/self.pps)] = 0
            
            if (not i == 0):
                self.data[int(nextX/self.pps)][int(nextY/self.pps)] = 1
                
                
                
                tail.move(nextX - tail.getPos()[0], nextY - tail.getPos()[1] )
            else:
                print 
                
                tail.move((pos[0] - tail.getPos()[0]),(pos[1]-tail.getPos()[1]))
                self.data[int(tail.getPos()[0]/self.pps)][int(tail.getPos()[1]/self.pps)] =1
            
            
        
        self.oldPos = self.position
        return
        
    def getRect(self):
        
        return self.head

    def getTail(self):
        
        return self.body
        
    def getCoords(self):
        
        return self.coords
        
    def getData(self):
        
        return self.data
        
    def addTail(self, direction):
        self.body.append(Tail((self.position[0]-direction[0],self.position[1]-direction[1]), self.pps))
        return
        
    pass

