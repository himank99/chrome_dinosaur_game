import pygame
import random
import sys
import os
import select
from message import decode_msg_size
from pygame.locals import *    # For userevents to place obstacles
pygame.init()                   #must be there to start the game
win_size = W,H = 640,480                #width and heigth of the game window
win = pygame.display.set_mode(win_size)     #my window size
pygame.display.set_caption("DINO GAME")         #Game name appears on the bar
bg = pygame.image.load('images/bg.png').convert()       #load the background(land surface)
game = pygame.image.load('images/gameover.png')
restart = pygame.image.load('images/re.png')
bgX1 = 0                                    #using to background images one after another
bgX2 = bg.get_width()

clock = pygame.time.Clock()

white = 255,255,255
black = 0,0,0

def get_message(fifo: int) -> str:
    msg_size_bytes = os.read(fifo, 4)
    msg_size = decode_msg_size(msg_size_bytes)
    msg_content = os.read(fifo, msg_size).decode("utf8")
    return msg_content

class Dino():
    run = [pygame.image.load('images/tRex/1.png'),pygame.image.load('images/tRex/2.png')]   # load the running images
    run_list = [0,0,0,1,1,1]                                    #add more 0s and 1s to slow down the graphis of legs of dino
    jump = pygame.image.load('images/tRex/0.png')               #load the jump images
    jumpList = [1,1,1,2,2,2,2,3,3,3,3,3,4,4,4,4,4,0,0,0,0,-1,-1,-1,-2,-2,-2,-2,-3,-3,-3,-3,-3,-4,-4,-4,-4,-4]  #list of jump step,addded miltiple numbers to slow down the graphis,change of position
    duck = [pygame.image.load('images/tRex/4.png'),pygame.image.load('images/tRex/5.png')]
    duck_list = [0,0,0,1,1,1]
    def __init__(self,x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.jumping = False
        self.ducking = False
        self.jumpCount = 0
        self.runCount = 0
        self.gameover = False
    def draw(self,win):         #to draw the dino on scree
        if self.jumping:
            self.y -= self.jumpList[self.jumpCount]*5
            win.blit(self.jump,(self.x,self.y))
            self.jumpCount+=1
            if self.jumpCount > len(self.jumpList)-1:
                self.jumpCount = 0
                self.jumping = False
            self.hitbox = (self.x, self.y, self.width + 55, self.height+60)         #create the collison box
            #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)       # to draw rectangular boxes around the object to check collisons
        else :
            if self.ducking:
                if self.runCount > len(self.duck_list)-1:
                    self.runCount = 0
                win.blit(self.duck[self.duck_list[self.runCount]],(self.x,self.y+35))
                self.ducking = False
                self.runCount+=1
                self.hitbox = (self.x, self.y+35, self.width+85, self.height+30)
                #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
            else :
                if self.gameover == True:
                  win.blit(pygame.image.load('images/tRex/3.png'),(self.x,self.y))
                else:
                    if self.runCount > len(self.run_list)-1:
                        self.runCount = 0
                    win.blit(self.run[self.run_list[self.runCount]],(self.x,self.y))
                    self.runCount+=1
                    self.hitbox = (self.x, self.y, self.width + 55, self.height + 60)
                    #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
class cactus1():    #class of small size cactus
    small_list = [pygame.image.load('images/obstacles/small/' + str(x) + '.png') for x in range(1,5)]
    
    def __init__(self,x,y,width,height,dist,c):
        self.x = x
        self.y = y
        self.c = c
        self.width = width
        self.height = height
        self.dist = dist
    def draw(self,win):
        self.hitbox = (self.x + self.dist*self.width, self.y+15, self.width, self.height+35)
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(self.small_list[self.c],(self.x+self.dist*self.width,self.y+15))
        
    def collide(self,rect):
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] + rect[3] > self.hitbox[1]:
                return True
        return False
        
        
class cactus2(cactus1):     #large size cactus
    large_list = [pygame.image.load('images/obstacles/large/' + str(x) + '.png') for x in range(1,6)]
    def draw(self,win):
        self.hitbox = (self.x+self.dist*self.width,self.y-5,self.width+15,self.height+45)
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(self.large_list[self.c],(self.x+self.dist*self.width,self.y-5))
    def collide(self,rect):
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] + rect[3] > self.hitbox[1]:
                return True
        return False
        
class bird():
    bird_img = [pygame.image.load('images/obstacles/bird1.png'),pygame.image.load('images/obstacles/bird2.png')]
    
    bird_list = [0,0,0,1,1,1]
    def __init__(self,x,y,width,height,r3):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bird_count = 0
        self.position = r3
    
    def draw(self,win):
        if self.bird_count > len(self.bird_list)-1:
            self.bird_count = 0
        if self.position == 0:      #bird is near to the ground (to jump)
            self.hitbox = (self.x, self.y+30 , self.width+30,self.height+30)
            #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
            win.blit(pygame.transform.scale(self.bird_img[self.bird_list[self.bird_count]],(64,64)),(self.x,self.y+30))
        else :
            if self.position == 1:  #above from the ground (to duck)
                self.hitbox = (self.x, self.y-50 , self.width+30,self.height+10)
                #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
                win.blit(pygame.transform.scale(self.bird_img[self.bird_list[self.bird_count]],(64,64)),(self.x,self.y-50))
        if dino.gameover == False:  #game is still going then else bird stops moving
            self.bird_count+=1
    def collide(self,rect):     #collision for both kind of birds
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if self.position == 1:
                if rect[1] < self.hitbox[3]:
                    return True
            else:
                if self.position == 0:
                    if rect[1] + rect [3] > self.hitbox[1]:
                        return True
        return False
        
#TO DO : create highest score file and load each time and after quiting delete that file
def num(score):
    res = list(map(int, str(score)))
    for i in range(5-len(res)):
        res = [0] + res
    return res
class score1(): #to maintain scoreboard
    numbers = [pygame.image.load('images/score/' + str(x) + '.png') for x in range(0,10)]
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.count_list = []
    def draw(self,win):
        win.blit(pygame.image.load('images/score/hi.png'),(self.x - 50,self.y))
        self.count_list = num(score)   # to convert the number into list of numbers
        for i in range(0,5):
            win.blit(self.numbers[self.count_list[i]],(self.x + i*20,self.y))
        
        
def redraw():       # function to draw everything on screen
    win.fill(black)     #to paint screen black
    win.blit(bg,(bgX1,H-100))       #draw ground
    win.blit(bg,(bgX2,H-100))
    scoreboard.draw(win)
    #font = pygame.font.Font('freesansbold.ttf', 16)
    #text = font.render('HI ' + str(score), 1, (255,255,255))
    dino.draw(win)      #dino on screen
    #cac.draw(win)
    for x in obstacles:
        x.draw(win)
    #win.blit(text,(500,10))
    if dino.gameover == True:
        win.blit(game,(W/2-190,H/2-70))     #gameover sign
        win.blit(restart,((W/2-30,H/2)))    #restart logo appears on screen
    pygame.display.update()         #neccessary to update after adding contents
score = 0       #initialize score to 0
gameover = False
dino = Dino(100,H-170,32,32)    #create dino instance
scoreboard = score1(W-150,20)   # to maintain score on top right
obstacles = []
pygame.time.set_timer(USEREVENT+1, random.randrange(3000,3500)) #user event which triggers after 3sec to 3.5sec to create obstacles on the ground
while True:

    for obstacle in obstacles:
        #if obstacle.x < -obstacle.width:
            #obstacles.pop(obstacles.index(obstacle))
            
        #else:
        if obstacle.collide(dino.hitbox):       #each time check for collisons
            dino.gameover = True
        if dino.gameover == False:
            obstacle.x -= 20        #same speed as ground
    if dino.gameover == False:
        score +=1   #increase the score if game is on
        bgX1 -= 20
        bgX2 -= 20
    if bgX1 < -bg.get_width():
        bgX1 = bg.get_width()
    if bgX2 < -bg.get_width():
        bgX2 = bg.get_width()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:   #to quit the game using red cross
            poll.unregister(fifo)
            os.close(fifo)
            os.remove(IPC_FIFO_NAME)
            pygame.quit()
            quit()
        if event.type == USEREVENT+1:
            br = 2
            if score > 300: #birds are allowed after score of 300
                br = 3
            r = random.randrange(0,br)
            if r == 0:
                r1 = random.randrange(1,4)  # how many small cactus obstacles
                if r1 == 1:
                    obstacles.append(cactus1(W,H-170,32,32,0,random.randrange(0,4)))
                elif r1 == 2:
                    obstacles.append(cactus1(W,H-170,32,32,0,random.randrange(0,4)))
                    obstacles.append(cactus1(W,H-170,32,32,1,random.randrange(0,4)))
                elif r1 == 3:
                    obstacles.append(cactus1(W,H-170,32,32,0,random.randrange(0,4)))
                    obstacles.append(cactus1(W,H-170,32,32,1,random.randrange(0,4)))
                    obstacles.append(cactus1(W,H-170,32,32,2,random.randrange(0,4)))
            elif r == 1:
                r2 = random.randrange(1,3)
                if r2 == 1:
                    obstacles.append(cactus2(W,H-170,32,32,0,random.randrange(0,5)))
                if r2 == 2:
                    obstacles.append(cactus2(W,H-170,32,32,0,random.randrange(0,5)))
                    obstacles.append(cactus2(W,H-170,32,32,1,random.randrange(0,5)))
            elif r == 2 :
                r3 = random.randrange(0,2)
                obstacles.append(bird(W,H-170,32,32,r3))
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_SPACE] or keys[pygame.K_UP]:   #game controls from keyboard
        flag = False
        if dino.gameover == True :      #if game is over start again after pressing space bar
            dino = Dino(100,H-170,32,32)
            obstacles = []
            bgX1 = 0
            flag = True
            bgX2 = bg.get_width()
            score = 0
        else:
            if not(dino.jumping) and flag==False:
                dino.jumping = True
    if keys[pygame.K_DOWN]:
        if not(dino.ducking):
            dino.ducking = True
    #clock.tick(30)
    redraw()



