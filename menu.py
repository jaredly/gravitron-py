import time
import pygame
from pygame.locals import *


class Menu:
    def __init__(self,screen,title,buttons,fgc=(0,0,0),mgc=(200,200,200),bgc=(255,255,255),hgc=(100,100,100),size=40,font=None,sub=''):
        self.top = pygame.font.Font(font,size).render(title,True,mgc,bgc)
        self.width = screen.get_rect().width
        self.height = screen.get_rect().height
        midx = self.width/2
        midy = self.height/2
        bh = (size/2+10)
        th = len(buttons)*bh
        self.selected = 0
        if not sub:
            self.sub = None
            sh = 0
            self.spos = 0,0
        else:
            self.sub = pygame.font.Font(font,size/3).render(sub,True,mgc,bgc)
            sh = self.sub.get_rect().height+10
            self.spos = midx-self.sub.get_rect().width/2, midy-th/2-10-sh
        self.tpos = (midx-self.top.get_rect().width/2,midy-th/2-10-sh-self.top.get_rect().height)
        self.buttons = []
        for i,b in enumerate(buttons):
            if type(b)==str:
                b = [b,b]
            self.buttons.append( MenuButton(self,b[0],b[1],i,self.width/2,self.height/2-th/2+i*bh,False,fgc,hgc,bgc,size/2,cx=1) )
        self.buttons[0].hover = True
        self.bgc = bgc
        self.fgc = fgc

    def draw(self,screen):
        screen.blit(self.top,self.tpos)
        if self.sub:
          screen.blit(self.sub,self.spos)
        [b.draw(screen) for b in self.buttons]

    def step(self):
        pass

    def event(self,event):
        if event.type==QUIT:
            self.running = False
        elif event.type==KEYDOWN:
            if event.key == K_DOWN:
                self.buttons[self.selected].hover = False
                self.selected += 1
                if self.selected >= len(self.buttons):
                    self.selected = 0
                self.buttons[self.selected].hover = True
            elif event.key == K_UP:
                self.buttons[self.selected].hover = False
                self.selected -= 1
                if self.selected < 0:
                    self.selected = len(self.buttons)-1
                self.buttons[self.selected].hover = True
            elif event.key in (K_RETURN,K_SPACE):
                self.buttons[self.selected].action()
        [b.event(event) for b in self.buttons]

    def events(self):
        [self.event(event) for event in pygame.event.get()]

    def loop(self,screen):
        self.ret = False, False
        self.running = True
        screen.fill(self.bgc)
        while self.running:
            self.events()
            self.draw(screen)
            pygame.display.flip()
        return self.ret

class Button:
    def __init__(self,parent,text,value,index,x,y,action,fgc=(0,0,0),mgc=(200,200,200),bgc=(255,255,255),size=35,margin=[10,5],cx=0,cy=0):
        self.font = pygame.font.Font(None,size)
        self.action = action
        self.parent = parent
        self.text = text
        self.value = value
        self.index = index
        w,h = self.font.size(text)
        x-=(w/2+margin[0])*cx
        y-=(h/2+margin[1])*cy
        self.rect = Rect(x,y,w+margin[0]*2,h+margin[1]*2)
        
        img = pygame.Surface((w+margin[0]*2,h+margin[1]*2))
        img.fill(bgc)
        img.blit(self.font.render(text,True,fgc,bgc),margin)
        #pygame.draw.rect(img,fgc,(0,0,w+margin[0]*2,h+margin[1]*2),3)
        
        img2 = pygame.Surface((w+margin[0]*2,h+margin[1]*2))
        img2.fill(bgc)
        img2.blit(self.font.render(text,True,mgc,bgc),margin)
        #pygame.draw.rect(img2,mgc,(0,0,w+margin[0]*2,h+margin[1]*2),3)
        
        img3 = pygame.Surface((w+margin[0]*2,h+margin[1]*2))
        img3.fill(bgc)
        img3.blit(self.font.render(text,True,mgc,bgc),margin)
        #pygame.draw.rect(img3,fgc,(0,0,w+margin[0]*2,h+margin[1]*2),3)
        self.img = [img,img2,img3]
        self.hover = 0
        self.clicked = False
        
    def draw(self,screen):
        screen.blit(self.img[self.hover],self.rect.topleft)

    def event(self,event):
        if event.type==MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if not self.hover:
                    self.hover = 1
                    self.parent.buttons[self.parent.selected].hover = 0
                    self.parent.selected = self.index
            #else:
            #    self.hover = 0
        elif event.type==MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.hover = 2
                self.clicked = True
        elif event.type==MOUSEBUTTONUP:
            if self.clicked and self.rect.collidepoint(event.pos):
                self.action()
                self.hover = 0
            self.clicked = False
    
    def step(self):
        pass

class MenuButton(Button):
    def __init__(self,parent,*a,**b):
        Button.__init__(self,parent,*a,**b)
        def meta():
            self.parent.running = False
            self.parent.ret = self.text,self.value
        self.action = meta

def WaitScreen(screen,text,wait,fgc=(0,0,0), bgc=(255,255,255), size=40):
    txt = pygame.font.Font(None,size).render(text,True,fgc,bgc)
    w,h = txt.get_rect().size
    m,n = screen.get_rect().center
    screen.fill(bgc)
    screen.blit(txt,(m-w/2,n-h/2))
    pygame.display.flip()
    time.sleep(wait)

if __name__=="__main__":
    pygame.init()
    scr = pygame.display.set_mode((200,200))
    m = Menu(scr,"Test",['Menu','Test','Click','Here'])
    print m.loop(scr)

