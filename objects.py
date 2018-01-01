import pygame
from pygame.locals import *
import math,random,time

from PIL import Image,ImageDraw

from gamebase import BaseSprite
from sprite import ImageSprite, Sprite, Vector, dst, dstpos, angle_to, rotate_polygon, move_polygon


class Spot(ImageSprite):
    maxhp = 20
    maxlives = 3
    def __init__(self, parent, pos):
        ImageSprite.__init__(self, parent, pos, "images/square.png")
        self.hp = self.maxhp
        self.lives = self.maxlives
    def step(self):
        if self.v.m > 10:
            self.v.m = 10
        keys = pygame.key.get_pressed()
        dirs = {K_RIGHT:0,K_DOWN:90,K_LEFT:180,K_UP:270}
        moving = False
        for k, d in dirs.items():
            if keys[k]:
                self.v += Vector(dirs[k], 2, 1)
                moving = True
        if not moving:
            self.v.m *= .8
        super(Spot,self).step()
        for obj in self.parent.objects:
            if isinstance(obj, Enemy):
                dt = dstpos(self.pos,obj.pos)
                if dt < self.size+obj.size:
                    v = Vector(angle_to(obj.pos,self.pos), - (dt - self.size - obj.size))
                    self.pos[0]+=v.x()
                    self.pos[1]+=v.y()
        self.limit_pos([0,0]+list(self.parent.size))
    def addHealth(self,x):
        self.hp+=x
        if self.hp>self.maxhp:
            self.hp = self.maxhp
    def damage(self,amount):
        self.hp -= amount
        if self.hp<=0:
            self.kill()
            self.parent.add(SpotExplosion(self.parent,self.pos))
    def loseLife(self):
        if self.lives>1:
            self.lives -= 1
            self.hp = self.maxhp
            self.parent.restartLevel()
        else:
            self.parent.lost()

class Bullet(ImageSprite):
    _image = "images/bullet.png"
    maxspeed = 12
    color = 250,250,0
    damage = 1
    def __init__(self,parent,pos,v = 5):
        ImageSprite.__init__(self,parent,pos,self._image)
        self.size = 5
        self.tail = [pos[:] for x in range(10)]
        if isinstance(v, Vector):
            self.v = v
        else:
            if v is None:
                v = self.maxspeed
            self.v = Vector(angle_to(self.pos, self.parent.spot.pos), v)
        self.inbad = True
    def step(self):
        inbad = False
        for obj in self.parent.objects:
            if obj is self:continue
            if isinstance(obj, Spot):
                self.collideSpot(obj)
            elif isinstance(obj, Enemy):
                if self.collideEnemy(obj):
                    inbad = True
            elif isinstance(obj, Bullet):
                if self.collideSelf(obj):
                    inbad = True
        if self.inbad and  not inbad:
            self.inbad = False
        if self.v.m > self.maxspeed:
            self.v.m = self.maxspeed
        old = self.pos[:]
        super(Bullet,self).step()
        for i in range(len(self.tail)-1,0,-1):
            self.tail[i] = self.tail[i-1]
        self.tail[0] = old
    def collideEnemy(self,obj):
        dp = dstpos(self.pos,obj.pos)
        if dp < obj.size+self.size:
            if self.inbad:
                return True
            self.kill()
            obj.damage(self.damage)
        self.v += Vector(angle_to(self.pos,obj.pos), 20/dp)
    def collideSpot(self,obj):
        dp = dstpos(self.pos,obj.pos)
        if dp < obj.size+self.size:
            obj.damage(self.damage)
            self.kill()
        self.v += Vector(angle_to(self.pos,obj.pos), 100/dp)
    def collideSelf(self,obj):
        if dstpos(self.pos,obj.pos)<self.size*2:
            if self.inbad:
                return True
            self.kill()
            obj.kill()
            self.parent.addScore(30)
    def kill(self,explode=True):
        super(Bullet,self).kill()
        if explode:
            self.parent.objects.append( Explosion( self.parent, self.pos ) )
        #print self.tail
    def draw(self,screen):
        ## draw tail
        #pygame.draw.lines(screen, self.color, 0, self.tail)
        ## draw off screen arrow
        x,y = self.pos
        if x<-self.size:x=0
        if x>self.parent.size[0]+self.size:
            x = self.parent.size[0]
        if y<-self.size:y=0
        if y>self.parent.size[1]+self.size:
            y = self.parent.size[1]
        if [x,y] == self.pos:
            return ImageSprite.draw(self,screen)
        if x == 0:
            angle = 0
        elif x == self.parent.size[0]:
            angle = math.pi
        elif y == 0:
            angle = math.pi/2
        else:
            angle = math.pi*3/2
        poly = (0,0), (8,-4), (8,4)
        poly = rotate_polygon(poly, angle)
        poly = move_polygon(poly, (x,y))
        pygame.draw.polygon(screen, self.color, poly, 1)

class Bullet2(Bullet):
    _image = "images/bullet2.png"
    maxspeed = 15
    color = 255,0,0
    damage = 2
    def __init__(self,*a,**b):
        Bullet.__init__(self,*a,**b)
        self.v.m = self.maxspeed

class Vine(Bullet):
    _image = "images/vine.png"
    color = 0,255,0
    def __init__(self,parent,pos,v=None, twin=None):
        if twin:
            self.twin = twin
            twin.twin = self
        Bullet.__init__(self,parent,pos, v)
    def collideSelf(self,obj):
        if obj is self.twin:
            dp = dstpos(self.pos,obj.pos)
            self.v += Vector(angle_to(self.pos,obj.pos), dp/50.0)
            return False
        else:
            return Bullet.collideSelf(self, obj)

class Vine2(Bullet):
    _image = "images/vine2.png"
    color = 0,255,0
    maxspeed = 15
    damage = 2
    def __init__(self,parent,pos,v=None, twin=None):
        if twin:
            self.twin = twin
            twin.twin = self
        Bullet.__init__(self,parent,pos, v)
        self.v.m = self.maxspeed
    def collideSelf(self,obj):
        if obj is self.twin:
            dp = dstpos(self.pos,obj.pos)
            self.v += Vector(angle_to(self.pos,obj.pos), dp/50.0)
            return False
        else:
            return Bullet.collideSelf(self, obj)

class Health(ImageSprite):
    def __init__(self,parent):
        where = random.randrange(4) # top, left, bottom, right
        pos1 = random.randrange(parent.size[0])
        if where==0:
            pos = [pos1, -20]
        elif where==1:
            pos = [-20,pos1]
        elif where==2:
            pos = [pos1, parent.size[1]+20]
        else:
            pos = [parent.size[0]+20, pos1]
        ImageSprite.__init__(self, parent, pos, "images/health.png")
        self.v = Vector(angle_to(self.pos, [parent.size[0]/2,parent.size[1]/2]), 5)
        self.out = True
    def step(self):
        ImageSprite.step(self)
        if dstpos(self.pos,self.parent.spot.pos)<self.size+self.parent.spot.size:
            self.parent.spot.addHealth(2)
            self.kill()
        if not pygame.Rect(0,0,self.parent.size[0],self.parent.size[1]).colliderect((self.pos[0]-self.size, self.pos[1]-self.size, self.size*2,self.size*2)):
            if not self.out:
                self.kill()
        else:
            self.out = False

class Explosion(ImageSprite):
    def __init__(self,parent,pos):
        ImageSprite.__init__(self,parent,pos,'images/bullet.png')
        self.time = 1
    def step(self):
        self.time+=.2
        if self.time>5:
            self.kill()
    def draw(self,screen):
        nimg = pygame.transform.scale(self.image(), (int(self.size*self.time), int(self.size*self.time)))
        screen.blit(nimg, (self.pos[0]-self.size*self.time/2, self.pos[1]-self.size*self.time/2))
    def kill(self):
        if self in self.parent.objects:
            self.parent.objects.remove(self)
        self.parent.check_done()
class SpotExplosion(Explosion):
    def kill(self):
        if self in self.parent.objects:
            self.parent.objects.remove(self)
        self.parent.spot.loseLife()

class Enemy(Sprite):
    def kill(self):
        Sprite.kill(self)
        self.parent.check_done()

class Grunt(Enemy):
    ival = 160
    size = 20
    speed = 10
    color = (250,250,0)
    bspeed = 20
    hp = 1
    points = 100
    def __init__(self,parent,pos):
        Enemy.__init__(self,parent,pos)
        self.timer = random.randrange(self.ival)
        self.health = self.hp
        self.himg = None
    def step(self):
        self.timer+=1
        v = Vector( angle_to(self.pos,self.parent.spot.pos), self.speed )
        if self.timer>self.ival:
            self.timer=0
            self.fire()
        v.m*=.2
    def fire(self):
        self.firebullet()
    def firebullet(self, angle = 0, speed = 5, typ = Bullet, **args):
        v = Vector( angle_to(self.pos,self.parent.spot.pos) + angle, self.size )
        b = typ(self.parent, (self.pos[0]+v.x() , self.pos[1]+v.y() ), Vector(v.theta, self.bspeed), **args)
        self.parent.objects.append( b )
        return b
    def draw(self,screen):
        x, y = self.pos
        pygame.draw.circle(screen, self.color, [int(x), int(y)], self.size, 1)
        if self.hp > 1:
            sz = 10
            if self.himg is None:
                img = Image.new("RGB", (30,30), (0,0,0,0))
                draw = ImageDraw.Draw(img)
                for i in range(self.hp):
                    if i<self.health:
                        draw.pieslice( (0, 0, sz*2, sz*2), 360/self.hp*i, 360/self.hp * (i+1), outline = None, fill = self.color)
                    draw.line(((sz,sz), (sz + math.cos(math.pi*2/self.hp*i) * sz, sz + math.sin(math.pi*2/self.hp*i) * sz)), fill=(0,0,0), width = 1)
                mode = img.mode
                size = img.size
                data = img.tostring()
                surface = pygame.image.fromstring(data, size, mode)
                surface.set_colorkey((0,0,0))
                self.himg = surface
            screen.blit( self.himg, (self.pos[0] - sz, self.pos[1] - sz) )
    def damage(self,amount):
        self.health -= 1
        self.himg = None
        if self.health <= 0:
            self.kill()
    def kill(self):
        Enemy.kill(self)
        self.parent.addScore( self.points )
        #self.parent.objects.append(BadMan(self.parent,(50,50)))

class RedDeamon(Grunt):
    ival = 100
    hp = 2
    points = 150
    color = (250,0,0)

class Bad3(Grunt):
    ival = 40
    color = (0,0,250)
    points = 150
    size = 15
    speed = 12
    bspeed = 23

class Triclops(Grunt):
    ival = 180
    color = (0,255,0)
    hp = 3
    points = 200
    def fire(self):
        self.firebullet()
        self.firebullet(math.pi / 6)
        self.firebullet(-math.pi / 6)

class TriclopsBoss(Triclops):
    size = 30
    hp = 5
    points = 400
    def fire(self):
        self.firebullet(typ=Bullet2)
        self.firebullet(math.pi / 6,typ=Bullet2)
        self.firebullet(-math.pi / 6,typ=Bullet2)

class Vineman(Grunt):
    size = 20
    hp = 4
    points = 120
    color = 100,200,250
    def fire(self):
        tw = self.firebullet(math.pi / 3, typ=Vine)
        self.firebullet(-math.pi / 3, typ=Vine, twin = tw)

class VinemanBoss(Grunt):
    size = 30
    hp = 8
    points = 300
    color = 100,200,250
    def fire(self):
        tw = self.firebullet(math.pi / 2, typ=Vine2)
        self.firebullet(math.pi/6, typ=Vine2, twin=tw)
        tw = self.firebullet(-math.pi /2, typ=Vine2)
        self.firebullet(-math.pi/6, typ=Vine2, twin=tw)
        tw = self.firebullet(math.pi / 6, typ=Vine2)
        self.firebullet(-math.pi / 6, typ=Vine2, twin = tw)

class MiniSpike(Bullet):
    _image = "images/spike.png"
    color = 255,255,255
    def __init__(self,parent, pos, creator, angle, dist):
        Bullet.__init__(self,parent,pos)
        self.angle = angle
        self.creator = creator
        self.dst = dist
    def step(self):
        Bullet.step(self)
        self.angle += 5.0 / self.dst
        self.dst += .2
        self.pos = [self.creator.pos[0] + math.cos(self.angle)*self.dst, self.creator.pos[1] + math.sin(self.angle) * self.dst]

class MineSweeper(Grunt):
    hp = 3
    ival = 100
    spikeval = 250
    color = 150,100,0
    def __init__(self, *a, **b):
        Grunt.__init__(self, *a, **b)
        self.spval = self.spikeval/4
        self.chillenz = []
    def step(self):
        Grunt.step(self)
        self.spval -= 1
        if self.spval <= 0:
            s = MiniSpike(self.parent, self.pos, self, 0, self.size+15)
            self.parent.objects.append(s)
            self.chillenz.append(s)
            self.spval = self.spikeval/2
    def kill(self):
        Grunt.kill(self)
        for o in self.chillenz:
            o.kill()

class Guppie(Grunt):
    ival = 60
    sval = 140
    color = 255, 0, 255
    size = 15
    points = 50
    def __init__(self,*a,**b):
        Grunt.__init__(self,*a,**b)
        self.spawnval = self.sval/2
        self.destpos = random.randrange(self.parent.size[0]), random.randrange(self.parent.size[1])
    def step(self):
        Grunt.step(self)
        self.spawnval -= 1
        if self.spawnval <= 0:
            self.spawnval = self.sval
            g = Guppie(self.parent, self.pos)
            g.spawnval = g.sval
            self.parent.objects.append(g)
        if dstpos(self.pos,self.destpos)<20:
            self.destpos = random.randrange(self.parent.size[0]), random.randrange(self.parent.size[1])
        v = Vector(angle_to(self.pos,self.destpos), 2)
        self.pos[0] += v.x()
        self.pos[1] += v.y()

class Monitor(Sprite):
    cache = {}
    font = None
    def render(self, *args):
        if not self.font:
            self.font = pygame.font.Font(None,20)
        if not self.cache.has_key(args):
            self.cache[args] = self.font.render(*args)
        return self.cache[args]
    def draw(self,screen):
        ## health
        pygame.draw.rect(screen, (250,250,0), (self.pos[0],self.pos[1], 100,15), 1)
        pygame.draw.rect(screen, (250,250,0), (self.pos[0],self.pos[1], self.parent.spot.hp * 100.0/self.parent.spot.maxhp,15))
        health = self.render('%d/%d'%(self.parent.spot.hp,self.parent.spot.maxhp), 1, (250,250,250))
        health_shadow = self.render('%d/%d'%(self.parent.spot.hp,self.parent.spot.maxhp), 1, (0,0,0))
        screen.blit(health_shadow, (self.pos[0] + 40+1, self.pos[1]+1))
        screen.blit(health, (self.pos[0] + 40, self.pos[1]))
        ## score
        txt = self.render('Score: %s'%self.parent.score, 1, (250,250,0))
        screen.blit(txt, (self.pos[0] + 110, self.pos[1]))
        w = txt.get_rect().w
        txt = time.strftime("%M:%S",time.gmtime(time.time() - self.parent.stime))
        txt = self.render(txt, 1, (250,250,0))
        screen.blit(txt, (self.pos[0] + 110 + w + 10, self.pos[1]))
        x = self.pos[0] + 110 + w + 10 + txt.get_rect().w + 10
        ## lives
        for i in range(self.parent.spot.maxlives):
            ## TODO: change to an image
            pygame.draw.circle( screen, (255,255,255), (x, self.pos[1]+7), 6, (i>=self.parent.spot.lives and 1 or 0) )
            x += 18

