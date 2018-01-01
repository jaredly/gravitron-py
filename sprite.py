import pygame
from pygame.locals import *
import math,random

def angle_to((x,y),(a,b)):
    return math.atan2(b-y, a-x)

def dst(x, y):
    return math.sqrt(x*x+y*y)

def dstpos((x,y), (a,b)):
    return dst(x-a, y-b)

def rot_around((x,y), (a,b), theta): # rotate the first around the second
    v = Vector.frompos((a,b),(x,y))
    v.theta += theta
    return a + v.x(), b + v.y()

def rotate_polygon(pts,angle):
    return [rot_around(pt,(0,0),angle) for pt in pts]

def move_polygon(pts,pt):
    return map((lambda (a,b):(a[0]+b[0],a[1]+b[1])),zip(pts, [pt for i in range(len(pts))]))

from gamebase import BaseSprite

class MovingSprite(BaseSprite):
    size = None
    def __init__(self,parent,pos):
        self.parent = parent
        self.pos = list(pos)
        self.v = Vector()
        self.rect = pygame.Rect(0,0,0,0)
    def step(self):
        self.pos[0] += self.v.x()
        self.pos[1] += self.v.y()

class Vector:
    def __init__(self, theta=0, m=0, degrees=False):
        if degrees:
            theta = math.pi/180 * theta
        self.theta = theta
        self.m = m
    @classmethod
    def frompos(self,x,y):
        if type(x) in (list,tuple):
            x,y = y[0]-x[0], y[1]-x[1]
        return Vector(math.atan2(y,x), dst(x,y))
    def x(self):
        return math.cos(self.theta)*self.m
    def y(self):
        return math.sin(self.theta)*self.m
    def __add__(self,o):
        x = self.x() + o.x()
        y = self.y() + o.y()
        return Vector.frompos(x, y)

class Sprite(MovingSprite):
    def kill(self):
        self.parent.remove(self)

class ImageSprite(Sprite):
    cache = {}
    def __init__(self,parent,pos,image):
        Sprite.__init__(self,parent,pos)
        self.setImage(image)
    def setImage(self,image):
        if not ImageSprite.cache.has_key(image):
            ImageSprite.cache[image] = pygame.image.load(image)
        self._image = image
        self.size = self.image().get_rect().w/2
    def draw(self,screen):
        w,h = self.image().get_rect().size
        screen.blit(self.image(), (self.pos[0] - w/2, self.pos[1] - h/2))
    def image(self):
        return ImageSprite.cache[self._image]
    def limit_pos(self,(x,y,w,h)):
        if self.pos[0]<x:self.pos[0]=x
        if self.pos[1]<y:self.pos[1]=y
        if self.pos[0]>x+w:self.pos[0]=x+w
        if self.pos[1]>y+h:self.pos[1]=y+h
