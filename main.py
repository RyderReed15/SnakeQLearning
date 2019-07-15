
import random
import pygame
import numpy as np
import math
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

from apple import Apple
from head import Head
from button import Button
from slider import Slider
from tkinter.filedialog import askopenfilename




# Map init
mapWidth = 48
mapHeight = 48 #measured in snake segments
pps = 10 #Pixels per snake segment







#Game Controls
isPlaying = False # If game is running
atTitle = True # if at title screen
isPlayer = False # If a player is playing vs the DQN
isPaused = False # if the game is paused
isApple = False # if an apple exists
preTraining = False
isDone = False
direction = (0,-1*pps) # direction the snake is traveling



#Rendering
pygame.font.init()
window = pygame.display.set_mode((mapWidth*pps*2+240, mapHeight*pps+240)) # Game window
borderWidth = 1 # Game outline
sliders = [] # Array of all the sliders
buttons = [] # Array of current buttons
border = None
titleText = pygame.font.Font(dir_path+'/fonts\joystixMonospace.ttf', 80) # Large Title Text
controls = None # Controls image - declared later
subText = pygame.font.Font(dir_path+'/fonts\joystixMonospace.ttf', 20) #Smaller pixel text

#Data to pass to DQN
data = [] # Map
hiddenLayers = 1
distanceData = [0,0,0,0]
aAngle = 0
model = None

#Game Objects
snakeHead = None 
apple = None
ax = 0 #Apple x coord
ay = 0 # Apple y coord

#Game Measurements
score = 0
tempScore = 0
tempDist = 0
highScore = 0
generations = 0
ticks = 10 #updates per seconds


# Creates the data list
for i in range(0,48):
    data.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])


# init
def initialize():   

    
    pygame.display.set_caption('Scalar', '')
    titleScreen()
    
    
# Loads title screen
def titleScreen():
    global titleText
    global subText
    global window
    global atTitle
    global isPlayer
    global isPaused
    global buttons
    global train, preTraining
    

    atTitle = True
    buttons = []
    
    buttons.append(Button(480, 250, 260, 60, "Load Model", subText, (255,255,255), "load"))
    buttons.append(Button(480, 330, 260, 60, "Play", subText, (255,255,255), "start"))
    buttons.append(Button(480, 410, 260, 60, "Train", subText, (255,255,255), "train"))
    buttons.append(Button(480, 490, 260, 60, "Quit", subText, (255,255,255), "quit"))
    
    
    
    clock = pygame.time.Clock()
    color = [255,0,0]
    while(atTitle):
        clock.tick(30)
        
        if (color[0] == 255):
            if (color[2] >= 1):
                color[2]-=1
            if (color[1] <= 254):
                color[1]+=1
        if (color[1] == 255):
            if (color[0] >= 1):
                color[0]-=1
            if (color[2] <= 254):
                color[2]+=1
        if (color[2] == 255):
            if (color[1] >= 1):
                color[1]-=1
            if (color[0] <= 254):
                color[0]+=1
                
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_BACKSPACE:
                    pygame.quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    check = button.getBounds()
                    if (event.pos[0] > check[0] and event.pos[0] < check[2] and event.pos[1] > check[1] and event.pos[1] < check[3] and event.button == 1):
                        if (button.getFuntion().upper() == "START"):
                            atTitle = False
                            isPlayer = True
                            isPaused = True;
                            startGame()
                            return
                        elif (button.getFuntion().upper() == "LOAD"):
                            l = loadModel()
                            return
                        elif (button.getFuntion().upper() == "QUIT"):
                            pygame.quit()
                        elif (button.getFuntion().upper() == "TRAIN"):
                            isPlayer = False
                            preTraining = False
                            return
                        
        
                
            
        window.fill((0,0,0))
        
        title = titleText.render('Scalar', True,  (color[0], color[1], color[2]))
        subTitle = subText.render('A Machine Learning Game', True,  (color[0], color[1], color[2]))
        for button in buttons:
            pygame.draw.rect(window, (60, 155, 155), button.getRect(), 0)
            window.blit(button.getText(), button.getTextPos())
        window.blit(title, (410, 50))
        window.blit(subTitle, (415, 140))
        
        
        
        pygame.display.update()
        
    return 

# Starts Game
def startGame():
    global ticks 
    global mapWidth
    global mapHeight
    global pps
    global window
    global isPlaying 
    global subText
    global snakeHead
    global isPlayer
    global data
    global highScore
    global score
    global controls
    global sliders
    global preTraining
    global border
    global buttons
    
    
    reset()
    controls = pygame.image.load(dir_path+ '\imgs\controls.png')
    
    buttons = []
    
    buttons.append(Button(0, 480, 481, 60, "Pause", subText, (255,255,255), "pause"))
    buttons.append(Button(0, 541, 481, 60, "Menu", subText, (255,255,255), "menu"))
    if (not (isPlayer) and sliders == []):
        sliders.append(Slider(500, 20, 300, 20, 'ticks', (100, 40), 'Ticks', subText))
    
    
    
    border = pygame.Rect(0-borderWidth, 0-borderWidth, mapWidth*pps+(2*borderWidth), mapHeight*pps+(2*borderWidth))
    isPlaying = True
    
    clock = pygame.time.Clock()
    window.fill((0,0,0))
    
    update(buttons, sliders)
    if (not preTraining):
        snakeHead.addTail(direction)
    while isPlaying:
        if (preTraining or not isPlayer):
            isPlaying = False
            return 
        else:
            clock.tick(ticks)
            update(buttons, sliders)
        
    if (not preTraining):
        lost = subText.render('GAME OVER', True, (200,200,200))
        if (score > highScore):
            highScore = score
        window.blit(lost, (180, 200))
        pygame.display.update()
        titleScreen()
    return

 

# Loads DQN models
def loadModel():
    
    global model, train, isPlayer, preTraining
    model = askopenfilename(initialdir = dir_path+"/models", filetypes = (("checkpoint files","*.index"),("all files","*.*")))
    isPlayer = False
    preTraining = False
    return
    

# Main update function - Args(The window surface to render on, snakeHead Object, game outline Rect, button array, slider array)
def update(buttons, sliders):
    global mapWidth
    global snakeHead
    global isApple
    global apple
    global direction
    global border
    global subText
    global data    
    global highScore
    global score
    global ax, ay
    global isPlayer
    global window
    global generations
    global distanceData, aAngle
    
    head = snakeHead
    textScore = subText.render('Score: '+ str(score), True, (200,200,200))
    textHighScore = subText.render('High Score: '+ str(highScore), True, (200,200,200))
    
    if (isPlayer):
        checkEvents(buttons, None)
    else:
        textGen = subText.render('Generation: '+ str(generations), True, (200,200,200))
        checkEvents(buttons, sliders)
        for slider in sliders:
            if (slider.getMoveable()):
                moveSlider(slider)
                slider.setText(slider.getString() + ": " + str(ticks))
    genApple()
    
    
    
    window.fill((0,0,0))
    
    for button in buttons:
            pygame.draw.rect(window, (60, 155, 155), button.getRect(), 0)
            window.blit(button.getText(), button.getTextPos())
    if (not isPlayer):
         for slider in sliders:
                pygame.draw.line(window,(60, 155, 155), (slider.getPos()[0], slider.getEnd()[1]), slider.getEnd(), 1)
                pygame.draw.circle(window, (60, 155, 155), slider.getCirclePos(), 8, 0)
                window.blit(slider.getText(), slider.getPos())
    
    if (isApple):
        pygame.draw.rect(window, (255, 0, 0), apple.getRect(), 0)
        
    drawTail(window, snakeHead)
    pygame.draw.rect(window, (0, 149, 238), head.getRect(), 0)
    pygame.draw.rect(window, (155,155,155), border, 1)
    if (isPlayer):
        window.blit(controls, (580, 100))
    else:
         window.blit(textGen, (0, 640))
    
    
    window.blit(textScore, (0, 610))
    window.blit(textHighScore, (220, 610))
   
    
    
    pygame.display.update()
    if (not isPaused):
        
        if (checkOOB(head)):
            return
            
            
        head.move(direction)
        checkLoss(head)
        data = head.getData() 
        
        eatApple(apple.getRect(), head)
        distanceData = calcData()
        aAngle = angleOf(snakeHead.getCoords(), (ax,ay))
        
    
    return




# Draws the snake tail
def drawTail(surface, head):
    tail = head.getTail()
    
    for i in range(0, len(tail)):
        pygame.draw.rect(surface, (100,100,100), tail[i].getRect(), 0)
    
    return


    

# Generates an apple
def genApple():
    global isApple
    global apple
    global ax, ay, data
    
    if (not isApple):
        ax = random.randint(0,mapWidth-1)
        ay = random.randint(0,mapHeight-1)
        if (not data[ax][ay] == 0):
            genApple()
            return 
        else:
            apple = Apple((ax,ay), pps)
        
            isApple = True
    return
    
# checks if the apple should be eaten - Args(apple object, snakeHead object)
def eatApple(apple, head):
    global isApple 
    global score
    global direction
    
    if (apple.left == head.getRect().left and apple.top == head.getRect().top):
        isApple = False
        score += 1
        
        head.addTail(direction)
    return


# Checks for input events - Args(buttons array, sliders array)
def checkEvents(buttons, sliders):
    global direction
    global isPaused
    global isPlaying
    
    events = pygame.event.get()
    if (not sliders == None):
        checkSliderEvents(sliders,events)
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                direction = (-1*pps,0)
            elif event.key == pygame.K_RIGHT:
                direction = (1*pps,0)
            elif event.key == pygame.K_UP:
                direction = (0,-1*pps)
            elif event.key == pygame.K_DOWN:
                direction = (0,1*pps)
            elif event.key == pygame.K_BACKSPACE:
                pygame.quit()
            elif event.key == pygame.K_SPACE:
                if (isPaused == False):
                    isPaused = True
                else:
                    isPaused = False
        elif event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    check = button.getBounds()
                    if (event.pos[0] > check[0] and event.pos[0] < check[2] and event.pos[1] > check[1] and event.pos[1] < check[3] and event.button == 1):
                        if (button.getFuntion().upper() == "PAUSE"):
                            if (isPaused == False):
                                isPaused = True
                            else:
                                isPaused = False
                        if (button.getFuntion().upper() == "MENU"):
                            isPlaying = False
                            titleScreen()
                            
# Checks to see if the game should end from running into tail - Args(snakeHead object)
def checkLoss(head):
    global mapWidth
    global mapHeight
    coords = head.getCoords()
    
    if (data[int(coords[0])][int(coords[1])] == 1):
        lose()
    
    return
    
# Checks to see if the game should end from going out of bound - Args(snakeHead object)
def checkOOB(head):
    global mapWidth
    global mapHeight
    global direction
    global isPlaying
    global pps
    
    coords = (head.getCoords()[0] + direction[0]/pps, head.getCoords()[1] + direction[1]/pps)
    if (coords[0] >= mapWidth or coords[1] >= mapHeight or coords[0] < 0 or coords[1] < 0):
        lose()
        return True
    else:
        return False
        

#Ends the game
def lose():
    global snakeHead
    global isPlaying 
    global isPlayer
    global atTitle
    global generations
    global score, highScore, tempDist
    global isDone
    if (preTraining):
        isDone = True
    if not isPlayer:
        tempDist = 0
        isPlaying = False
        generations+=1
        if score > highScore:
            highScore = score
        reset()
    else:
        isPlaying = False
    
    return 

    

    
# Checks events specifically for slider movement - Args(slider array, game events)
def checkSliderEvents(sliders, events):
    for event in events:
        
        if event.type == pygame.MOUSEBUTTONDOWN:
                for slider in sliders:
                    check = slider.getCirclePos()
                    if (event.pos[0] > check[0]-8 and event.pos[0] < check[0]+8 and event.pos[1] > check[1]-8 and event.pos[1] < check[1]+8 and event.button == 1):
                        slider.setMoveable(True)
                        
        elif event.type == pygame.MOUSEBUTTONUP:
                for slider in sliders:
                    if (event.button == 1):
                        slider.setMoveable(False)
                     
# Moves the slider to mouseX - Args(slider object)   
def moveSlider(slider):
    x = pygame.mouse.get_pos()[0]
    sliderX = slider.getCirclePos()[0]
    checks = slider.getChecks()
    if (x > slider.getPos()[0] and x < slider.getEnd()[0]):
        slider.setPos(x)
    elif (not x > slider.getPos()[0]):
        slider.setPos(slider.getPos()[0])
        
    elif (not x < slider.getEnd()[0]):
        slider.setPos(slider.getEnd()[0])
        
    if (sliderX >= slider.getPos()[0] and sliderX < checks[0]):
        changeSliderVariable(slider, 0)
    elif (sliderX >= checks[0] and sliderX < checks[1]):
        changeSliderVariable(slider, 1)
    elif (sliderX >= checks[1] and sliderX <= checks[2]):
        changeSliderVariable(slider, 2)
    return
    
# Updates the slider variable - Args(slider object, section int)
def changeSliderVariable(slider, sect):
    global ticks
    if slider.getVariable().upper() == 'TICKS':
        if sect == 0:
            ticks = 10
        elif sect == 1:
            ticks = 100
        elif sect == 2:
            ticks = 1000
        elif sect == 3:
            ticks = 1000
    
# Resets game to beginning
def reset():
    global data, score, snakeHead, isPlaying, isApple
    score = 0   
    for i in range(48):
            data[i] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    isApple = False
    snakeHead = Head((0, 149, 238),(mapWidth/2, mapHeight/2), pps)

  
  
#return reward for DQN
def getReward(action):
    global direction
    global sliders
    global buttons
    global ax,ay, snakeHead, tempScore, score, tempDist
    if np.argmax(action) == 0:
        direction = (-pps, 0)
    elif np.argmax(action) == 1:
        direction = (pps, 0)
    elif np.argmax(action) == 2:
        direction = (0, -pps)
    elif np.argmax(action) == 3:
        direction = (0, pps)
    wait = update(buttons, sliders)
    head = (snakeHead.getRect().left/pps, snakeHead.getRect().top/pps)
    add = 0
    if (not (math.sqrt(math.pow((ax-head[0]), 2)+math.pow((ay-head[1]), 2))) == 0):
        dist = 1/(math.sqrt(math.pow((ax-head[0]), 2)+math.pow((ay-head[1]), 2)))
        if dist >= tempDist:
            add += 1
        else:
            add -= 1
        tempDist = dist
    else:
        tempDist = 0
    if isPlaying == False:
        add = -10
        tempScore = 0
        score = 0
    if score > tempScore:
        tempScore = score
        add = 10
    
    return (add)
    
        
def getData():
    global distanceData, aAngle, data
    return [distanceData[0],distanceData[1],distanceData[2],distanceData[3],aAngle]
    
def setPreTraining(training):
    global preTraining   
    preTraining = training
    
def getDone():
    global isDone
    return isDone
    
def getPlaying():
    global isPlaying
    return isPlaying
    
def setPlaying(var):
    global isPlaying
    isPlaying = var
    return 
    
def getGen():
    global generations
    return generations
    
def calcData():
    global snakeHead, ax, ay, data
    snakePos = snakeHead.getCoords()
    snakePos = [int(snakePos[0]), int(snakePos[1])]
    distance = [0,0,0,0]
    xS1 = False
    xS2 = False
    yS1 = False
    yS2 = False
    for x in range(snakePos[0], 0, -1):
        if xS1 == False:
            if (data[x][snakePos[1]] == 1):
                distance[0] = snakePos[0]-x
                xS1 = True
    if xS1 == False:
        distance[0] = snakePos[0]+1
    for x in range(snakePos[0], 48):
        if xS2 == False:
            if (data[x][snakePos[1]] == 1):
                distance[3] = x-snakePos[0]
                xS2 = True
    if xS2 == False:
        distance[3] = 48 - snakePos[0]
   
    
    for y in range(snakePos[1], 0, -1):
        if yS1 == False:
            if (data[snakePos[0]][y] == 1):
                distance[1] = snakePos[1]-y
                yS1 = True
    if yS1 == False:
        distance[1] = snakePos[1]+1
    for y in range(snakePos[1], 48):
        if yS2 == False:
            if (data[snakePos[0]][y] == 1):
                distance[2] = y-snakePos[1]
                yS2 = True
    if yS2 == False:
        distance[2] = 48 - snakePos[1]
    
    return distance

def angleOf(p1, p2): 
    
    deltaY = (p1[1] - p2[1]);
    deltaX = (p2[0] - p1[0]);
    result = math.degrees(math.atan2(deltaY, deltaX)); 
    if result < 0:
        result = 360+result
    return result

    
#initialize()