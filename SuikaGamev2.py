# coding: utf-8
import os
os.chdir(os.getcwd())
import sys
import time
import random
import string
import numpy as np
import pygame
from pygame.locals import *
from Box2D import b2
class PhysicsObject():
    def __init__(self,type,isStatic):
        self.type = type
        self.isStatic = isStatic
        self.objectID = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    def getType(self):
        return self.type
    def getIsStatic(self):
        return self.isStatic
    def getObjectID(self):
        return self.objectID
class StaticLine(PhysicsObject):
    def __init__(self,type,isStatic,pos,world):
        super().__init__(type,isStatic)
        self.body = world.CreateStaticBody(position=(0, 0), 
            shapes=b2.edgeShape(vertices=[(pos['X1']/size,pos['Y1']/size), (pos['X2']/size, pos['Y2']/size)]))
        self.pos1 = np.array([pos['X1'], pos['Y1']],dtype=np.float)
        self.pos2 = np.array([pos['X2'], pos['Y2']],dtype=np.float)
    def getX1(self):
        return self.pos1[0]
    def getY1(self):
        return self.pos1[1]
    def getX2(self):
        return self.pos2[0]
    def getY2(self):
        return self.pos2[1]
    def getPos1(self):
        return self.pos1
    def getPos2(self):
        return self.pos2
    def getBody(self):
        return self.body
class DynamicCircle(PhysicsObject):
    def __init__(self, type, isStatic, mass, pos, world):
        super().__init__(type,isStatic)
        self.body = world.CreateDynamicBody(position=(pos['X']/size, pos['Y']/size), fixtures=b2.fixtureDef(shape=b2.circleShape(radius=pos['R']/size), density=1))
        self.pos = np.array([pos['X'], pos['Y']],dtype=np.float)
        self.r = pos['R']
        self.m = mass
        self.v = np.array([0,0],dtype=np.float)
        self.f = np.array([0,0],dtype=np.float)
    def getX(self):
        return self.body.transform.position[0]*size
    def getY(self):
        return self.body.transform.position[1]*size
    def getR(self):
        return self.r
    def getPos(self):
        return np.array(self.body.transform.position)*size
    def getBody(self):
        return self.body
    def popSelf(self,world):
        print('Destroyed!')
        world.DestroyBody(self.body)
        del self
class FruitCircle(DynamicCircle):
    def __init__(self, type, isStatic, mass, pos, world, fruitID):
        super().__init__(type, isStatic, mass, pos, world)
        self.fruitID = fruitID
    def getFruitID(self):
        return self.fruitID
size = 100
class PhysicsEngine():
    def __init__(self) :
        self.objects = []
        self.world = b2.world(gravity=(0, -10), doSleep=True)
    def createLine(self,isStatic,pos,world):
        if isStatic == True:
            self.objects.append(StaticLine(type='Line',isStatic=isStatic,pos=pos,world=world))
    def createCircle(self,isStatic,pos):
        if isStatic == False:
            self.objects.append(DynamicCircle(type='Circle',isStatic=isStatic,pos=pos))
    def getObjects(self):
        return self.objects
    def getStaticLineObjects(self):
        StaticLines = []
        GameObjects = self.getObjects()
        for GameObject in GameObjects:
            if GameObject.getType() == 'Line' and GameObject.getIsStatic() == True:
                StaticLines.append(GameObject)
        return StaticLines
    def getDynamicCircleObjects(self):
        DynamicCircles = []
        GameObjects = self.getObjects()
        for GameObject in GameObjects:
            if GameObject.getType() == 'Circle' and GameObject.getIsStatic() == False:
                DynamicCircles.append(GameObject)
        return DynamicCircles
    def popObject(self,objectID):
        for object in self.objects:
            if object.getObjectID() == objectID:
                object.popSelf(self.world)
offsetX,offsetY = 400,470
offsetX,offsetY = 960,800
dropLineLength,dropLineY = 400,440
FruitsColor = [(255,197,197),(255,197,220),(230,197,255),(255,227,197),(255,218,197),(255,197,207),
               (249,255,197),(255,197,232),(255,253,197),(232,255,197),(200,255,197)]
class SuikaEngine(PhysicsEngine):
    def __init__(self):
        super().__init__()
        self.preFruitID = 6
        self.removedObjectIDs = []
        self.createBascket()
        self.play()
    def createBascket(self):
        self.createLine(isStatic=True,pos={'X1':200,'Y1':400,'X2':200,'Y2':0},world=self.world)
        self.createLine(isStatic=True,pos={'X1':-200,'Y1':400,'X2':-200,'Y2':0},world=self.world)
        self.createLine(isStatic=True,pos={'X1':200,'Y1':0,'X2':-200,'Y2':0},world=self.world)
    def createFruit(self, pos, fruitID):
        self.objects.append(FruitCircle(type='Circle',isStatic=False,mass=1,pos=pos,world=self.world,fruitID=fruitID))
    def dropFruit(self,mouseX,mouseY):
        fruitID = self.preFruitID
        pos= {'X':mouseX,'Y':dropLineY,'R':fruitID*5+10}
        self.createFruit(pos, fruitID)
        self.preFruitID = random.randint(0,10)
    def detectCollision(self):
        Fruits = self.getDynamicCircleObjects()
        removableFruitIDs = []
        creatableFruits = []
        for i in  range(len(Fruits)):
            FruitA = Fruits[i]
            posA = FruitA.getPos()
            for j in  range(len(Fruits)-i-1):
                FruitB = Fruits[j+i+1]
                posB = FruitB.getPos()
                if np.linalg.norm(posB-posA) < FruitA.getR()+FruitB.getR():
                    if FruitA.getFruitID() == FruitB.getFruitID():
                        if FruitA.getObjectID() not in removableFruitIDs and FruitB.getObjectID() not in removableFruitIDs:
                            removableFruitIDs.append(FruitA.getObjectID())
                            removableFruitIDs.append(FruitB.getObjectID())
                            fruitID = FruitA.getFruitID()+1
                            pos= {'X':(posA+posB)[0]/2,'Y':(posA+posB)[1]/2,'R':fruitID*5+10}
                            creatableFruits.append({'pos':pos,'fruitID':fruitID})
        for objectID in removableFruitIDs:
            if objectID not in self.removedObjectIDs:
                print(len(self.getDynamicCircleObjects()))
                self.popObject(objectID)
                print(len(self.getDynamicCircleObjects()))
                print(removableFruitIDs,len(creatableFruits))
                self.removedObjectIDs.append(objectID)
        #for fruit in creatableFruits:
            #self.createFruit(fruit['pos'], fruit['fruitID'])
        
                    
    def render(self,screen,mouseX,mouseY):
        for Line in self.getStaticLineObjects():
            pygame.draw.line(screen, (255,219,90),
                (offsetX+Line.getX1(),offsetY-Line.getY1()),
                (offsetX+Line.getX2(),offsetY-Line.getY2()),16)
            pygame.draw.circle(screen,(255,219,90),(offsetX+Line.getX1()+1,offsetY-Line.getY1()+1),8)
            pygame.draw.circle(screen,(255,219,90),(offsetX+Line.getX2()+1,offsetY-Line.getY2()+1),8)
        for Fruit in self.getDynamicCircleObjects():
            pygame.draw.circle(screen,FruitsColor[Fruit.getFruitID()],(offsetX+Fruit.getX()+1,offsetY-Fruit.getY()),Fruit.getR())
        pygame.draw.line(screen, (255,247,219),
            (offsetX+mouseX,offsetY-dropLineY),
            (offsetX+mouseX,offsetY-0),4)
        pygame.draw.circle(screen,(255,255,255),(offsetX+mouseX,offsetY-dropLineY),20)
        return screen
    def play(self):
        pygame.init()
        screen = pygame.display.set_mode((1920, 1080))
        preTime = time.time()
        while True:
            mouseX, mouseY = pygame.mouse.get_pos()
            mouseX, mouseY = mouseX-offsetX, mouseY-offsetY
            if mouseX < -dropLineLength/2:
                mouseX = -dropLineLength/2
            elif dropLineLength/2 < mouseX:
                mouseX = dropLineLength/2
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    self.dropFruit(mouseX,mouseY)
                    
            deltaTime = preTime - time.time()
            preTime = time.time()
            self.world.Step(1/100, 10, 8)
            self.dropFruit(mouseX,mouseY)
            #self.detectCollision()
            screen.fill((255,243,200))
            screen = self.render(screen,mouseX,mouseY)
            pygame.display.update()
            time.sleep(1/100)
            

if __name__ == "__main__":
    SuikaEngine()