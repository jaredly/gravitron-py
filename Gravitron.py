import pygame
from pygame.locals import *
import math

import time
import random
from math import pi,sin,cos,tan,atan2

from gamebase import MenuGame
import gamebase
import menu

'''IDEAS:
Boss w/ rotating sheild
Boss that shoots out waves that push you bask (in addition to bullets)
'''


from objects import Enemy, Spot, Monitor, Explosion, Health
import objects

def angle_to((x,y),(a,b)):
    return math.atan2(b-y, a-x)

def dst(x, y):
    return math.sqrt(x*x+y*y)

def dstpos((x,y), (a,b)):
    return dst(x-a, y-b)

class HelpPage(gamebase.HelpPage):
    text = '''\
    Move around w/ the arrow keys. The bullets
    shot at you by the bad guys are gravitationally
    attracted to you and.....you have no weapons!
    So your mission, if you choose to accept it, is
    to redirect the bullets back at your enemies.
    That's pretty much it.'''
    bgc = 0,0,0
    fgc = 255,255,255
    hgc = 100,100,255


class Gravitron(MenuGame):
    bgc = 0,0,0
    fgc = 255,255,255
    mgc = 0,0,255
    hgc = 100,100,255
    def __init__(self,size=[700,700]):
        super(Gravitron,self).__init__('Gravitron',['Levels','Help'],font=None, size=size, sub="by Jared Forsyth")
        self.ltxt = None
        self.level_done = False
        self.level = 0
        self.ltimer = 0
        self.load_levels()
        #self.classes = {"BadMan":Grunt,"Bad2":Bad2,"Bad3":Bad3,"Triclops":Triclops,"Guppie":Guppie}

    def load_levels(self):
        txt = open("levels.dat").read().split("\n")
        self.levels = []
        for line in txt:
            if not line:continue
            if line.startswith('--'):
                self.levels.append([])
                continue
            name, pos = line.split(":")
            pos = pos.split(',')
            pos = int(pos[0]), int(pos[1])
            self.levels[-1].append((name.strip(), pos))
        #random.random(

    def menu_item(self,text,value):
        if text=="Help":
            HelpPage(self.size).loop()
        elif text=="Levels":
            levelmenu = menu.Menu(self.screen, "Choose Stage", [("Stage %d"%(i+1),i) for i in range(int(math.ceil(len(self.levels)/5.0)))]+["Back"],size=80,font=self.font,mgc=self.mgc, fgc=self.fgc, bgc=self.bgc, hgc=self.hgc)
            res = levelmenu.loop(self.screen)
            if res[0] in ("Back",False):
                return
            self.play(res[1]*5)
            #self.level = res[1]*5+1

    def start(self, level=0):
        self.monitor = Monitor(self, (0,0))
        self.spot = Spot(self, (self.size[0]/2, self.size[1]/2))
        self.objects = [self.spot]
        self.score = 0
        self.stime = time.time()
        self.level = level
        self.won = False
        self.nextLevel()

    def nextLevel(self):
        self.leveltxt = pygame.font.Font(None,40).render('Stage %d.%d'%(self.level/5+1, self.level%5+1),True,(0,0,255))
        self.ltxt = pygame.font.Font(None,40).render('%d.%d'%(self.level/5+1, self.level%5+1),True,(0,0,255))
        self.ltxt.set_alpha(10)
        self.level += 1
        self.level_done = False
        if self.level > len(self.levels):
            self.won = True
            menu.WaitScreen(self.screen,"You Won!!!!",2,bgc=(0,0,0),fgc=(255,255,255))
            return
        self.ltimer = 0
        for obj,pos in self.levels[self.level-1]:
          self.objects.append(objects.__dict__[obj](self, pos))

    def restartLevel(self):
        self.level_done = False
        self.objects = [self.spot]
        self.spot.pos = [self.size[0]/2,self.size[1]/2]
        self.ltimer = 0
        for obj,pos in self.levels[self.level-1]:
          self.objects.append(objects.__dict__[obj](self, pos))

    def check_done(self):
        for obj in self.objects:
            if isinstance(obj,(Enemy,Explosion)):
                return False
        self.level_done = True

    def lost(self):
        self.won = 0
        messages = "Sorry, try again"#"Do you have trouble walking?", "It must be hard, being you.", "How many times did you drop out of school?", "Maybe you should start with tic-tac-toe"
        menu.WaitScreen(self.screen,random.choice(messages),2,(255,255,255),(0,0,0))

    def step(self):
        self.ltimer+=1
        if self.level_done:
            #time.sleep(1)
            #menu.WaitScreen(self.screen,"Stage Cleared",1,(255,255,255),(0,0,0))
            self.nextLevel()
        MenuGame.step(self)

    def draw(self):
        MenuGame.draw(self)
        self.monitor.draw(self.screen)
        #for i in range(self.lines):
        #    pygame.draw.line(self.screen,(0,0,0),(10+i*10,10),(10+i*10,30))
        w,h=self.screen.get_rect().size
        #self.gun.draw(self.screen)
        self.screen.blit(self.ltxt,(w-50,10))
        #self.screen.blit(self.htxt,(20,h-self.htxt.get_rect().h-10))
        if self.ltimer<40:
            w,h = self.leveltxt.get_rect().size
            self.leveltxt.set_alpha(int((40-self.ltimer)/40.0*100))
            self.screen.blit(self.leveltxt, (self.size[0]/2-w/2, self.size[1]/2-h/2))

    def addScore(self, points):
        self.score += points
        if int((self.score-points) / 500) != int(self.score / 500):
            self.add(Health(self))

if __name__=='__main__':
    pygame.font.init()
    g = Gravitron((700,700))
    g.loop()
    pygame.quit()
