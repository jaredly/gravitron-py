import pygame
from pygame.locals import *

import menu

class Game(object):
    bgc = 255,255,255
    fullscreen = False
    def __init__(self,size=(500,500),fps=40):
        flags = 0
        if self.fullscreen:flags = FULLSCREEN
        self.screen = pygame.display.set_mode(size, flags)
        self.size = size
        self.objects = []
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.running = False
    def add(self,o):
        self.objects.append(o)
    def remove(self,o):
        if o in self.objects:
            self.objects.remove(o)
            return True
        return False
    def send(self,name,*a,**b):
        return [(getattr(o,name)(*a,**b) or 0) for o in self.objects]
    def event(self,event):
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            return self.quit()
        return self.send("event",event)
    def step(self):
        return self.send('step')
    def draw(self):
        return self.send('draw',self.screen)
    def events(self):
        [self.event(event) for event in pygame.event.get()]
    def quit(self):
        self.running = False
    def loop(self):
        self.running = True
        while self.running:
            self.screen.fill(self.bgc)
            self.events()
            self.step()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)

class MenuGame(Game):
    bgc = (255,255,255)
    fgc = (0,0,0)
    mgc = (0,0,255)
    hgc = 100,100,100
    pause_key = K_p
    def __init__(self,title,menu_items = [],font=None,size=(500,500), fps=40, sub=''):
        Game.__init__(self,size=size)
        self.won = False
        self.font=font
        self.title = title
        self.sub = sub
        self.paused = False
        self.menu_items = menu_items
        self.fps = fps
    def start(self):pass
    def end(self):pass
    def pause(self):
        self.paused = True
        txt = pygame.font.Font(None,50).render("paused",1,self.hgc)
        w,h = txt.get_rect().size
        self.screen.blit(txt, (self.size[0]/2 - w/2, self.size[1]/2 - h/2))
        pygame.display.flip()
    def unpause(self):
        self.paused = False
    def event(self, e):
        if e.type == KEYDOWN and e.key == self.pause_key:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        Game.event(self, e)
    def menu_item(self,callb):pass
    def play(self, *a):
        self.won = False
        self.start(*a)
        while self.won is False:
            self.events()
            if not self.paused:
                self.screen.fill(self.bgc)
                self.step()
                self.draw()
                pygame.display.flip()
            self.clock.tick(self.fps)
        self.end()
    def quit(self):
        self.won = -1
    def loop(self):
        self.running = True
        main_menu = menu.Menu(self.screen,self.title,['Start']+list(self.menu_items)+['Quit'],size=80,font=self.font,mgc=self.mgc, fgc=self.fgc, bgc=self.bgc, hgc=self.hgc, sub=self.sub)
        while self.running:
            res = main_menu.loop(self.screen)
            if res[0]=='Start':
                self.play()
            elif res[0] in ('Quit',False):
                self.running = False
                pygame.quit()
                break
            else:
                self.menu_item(*res)

class HelpPage(Game):
    text = '''\
Hello everybody im going to talk
right up until this wraps around
cause I jst want to thats why.

Here in the bush country we like
to eat grass and tell folk
tales untill one of us turns blue
in the face and calls "Uncle".'''
    img = None
    fgc = (0,0,0)
    bgc = (255,255,255)
    def __init__(self, size=(500,500)):
        Game.__init__(self,size=size)
        self.buttons = [menu.Button(self,'Back',None,0,10,10,self.quit,size=40,bgc=self.bgc,fgc=self.fgc)]
        self.selected = 0
        self.buttons[0].hover = True
        self.objects.append( self.buttons[0] )
        self.text = self.text.replace('\n\n','<br>').replace('\n',' ').replace('<br>','\n')
        self.font = pygame.font.Font(None,40)
    def event(self,e):
        Game.event(self,e)
        if e.type == KEYDOWN and e.key in (K_RETURN, K_ESCAPE):
            self.buttons[0].action()
    def draw(self):
        Game.draw(self)
        sz = self.screen.get_rect()
        w = sz.w-20
        lh = self.font.size('HIASD')[1]+5
        top = 60
        chunks = self.text.split('\n')
        lines = []
        for chunk in chunks:
            words = chunk.split(' ')
            while len(words):
                i = 1
                if len(lines)*lh<200 and self.img:tw = w-200
                else:tw = w
                while self.font.size(' '.join(words[:i+1]))[0] < tw and i<len(words):
                    i += 1
                lines.append(' '.join(words[:i]))
                words = words[i:]
        for i,line in enumerate(lines):
            self.screen.blit(self.font.render(line,True,self.fgc,self.bgc),(10,top+lh*i))
        if self.img:
            self.screen.blit(self.img,(sz.w-210,top-10))

class BaseSprite(object):
    def __init__(self):
        pass
    def draw(self,screen):pass
    def step(self):pass
    def event(self,event):pass

if __name__=='__main__':
    pygame.init()
    HelpPage().loop()
