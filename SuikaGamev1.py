# coding: utf-8
import os
os.chdir(os.getcwd())
import sys
import time
import random
import numpy as np
import pygame
from pygame.locals import *
from Box2D import b2
class PhysicsObject():
    def __init__(self,type,isFixed):
        self.type = type
        self.isFixed = isFixed
    def getType(self):
        return self.type
    def getIsFixed(self):
        return self.isFixed
class FixedLine(PhysicsObject):
    def __init__(self,type,isFixed,pos):
        super().__init__(type,isFixed)
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
class FreeCircle(PhysicsObject):
    def __init__(self, type, isFixed, mass, pos):
        super().__init__(type,isFixed)
        self.pos = np.array([pos['X'], pos['Y']],dtype=np.float)
        self.r = pos['R']
        self.m = mass
        self.v = np.array([0,0],dtype=np.float)
        self.f = np.array([0,0],dtype=np.float)
    def getX(self):
        return self.pos[0]
    def getY(self):
        return self.pos[1]
    def getR(self):
        return self.r
    def getMass(self):
        return self.m
    def getPos(self):
        return self.pos
    def getSpeed(self):
        return self.v
    def getForce(self):
        return self.f
    def setPos(self,Pos):
        self.pos = Pos
    def setSpeed(self,Speed):
        self.v = Speed
    def empower(self,force):
        self.f += force
    def reflect(self,deltaTime):
        self.v   += self.f*deltaTime
        self.pos += self.v*deltaTime
        self.f = np.array([0,0],dtype=np.float)
class FruitCircle(FreeCircle):
    def __init__(self, type, isFixed, mass, pos, fruitID):
        super().__init__(type, isFixed, mass, pos)
        self.fruitID = fruitID
    def getFruitID(self):
        return self.fruitID
gravity = np.array([0,-100],dtype=np.float)
elastic = 0.2
class PhysicsEngine():
    def __init__(self) :
        self.objects = []
    def createLine(self,isFixed,pos):
        if isFixed == True:
            self.objects.append(FixedLine(type='Line',isFixed=isFixed,pos=pos))
    def createCircle(self,isFixed,pos):
        if isFixed == False:
            self.objects.append(FreeCircle(type='Circle',isFixed=isFixed,pos=pos))
    def getObjects(self):
        return self.objects
    def getFixedLineObjects(self):
        FixedLines = []
        GameObjects = self.getObjects()
        for GameObject in GameObjects:
            if GameObject.getType() == 'Line' and GameObject.getIsFixed() == True:
                FixedLines.append(GameObject)
        return FixedLines
    def getFreeCircleObjects(self):
        FreeCircles = []
        GameObjects = self.getObjects()
        for GameObject in GameObjects:
            if GameObject.getType() == 'Circle' and GameObject.getIsFixed() == False:
                FreeCircles.append(GameObject)
        return FreeCircles
    def collisionCircleXLine(self,Circle,Line):
        posP = Circle.getPos()
        posA = Line.getPos1()
        posB = Line.getPos2()
        massP = Circle.getMass()
        speedP = Circle.getSpeed()
        disAB = np.linalg.norm(posB-posA)
        disAP = np.linalg.norm(posP-posA)
        disBP = np.linalg.norm(posP-posB)
        dotAB_AP = np.dot(posB-posA,posP-posA)
        dotAB_BP = np.dot(posB-posA,posP-posB)
        rotateAB = np.dot(posB-posA,np.array([[0,1],[-1,0]]))
        posAa = posA+(posB-posA)/disAB*((disAP-disBP)/2-5)
        posBb = posB+(posB-posA)/disAB*((disAP-disBP)/2+5)
        disAB = np.linalg.norm(posBb-posAa)
        disAaP = np.linalg.norm(posP-posAa)
        disBbP = np.linalg.norm(posP-posBb)
        #distance = (np.cross(posP,posB-posA)-np.cross(posA,posB))/np.linalg.norm(posB-posA)
        distance = np.cross(posP-posA,posP-posB)/np.linalg.norm(posB-posA)
        if 0 < dotAB_AP and dotAB_BP < 0:
            if 0 <= distance <= Circle.getR():
                posPP = posP+(posAa-posP)*disBbP/(disAaP+disBbP)+(posBb-posP)*disAaP/(disAaP+disBbP) + rotateAB/disAB*Circle.getR()*1.05
                speed = speedP-rotateAB*np.cross(posB-posA,speedP)*(1+elastic)/np.dot(posB-posA,posB-posA)
                Circle.setPos(posPP)
                Circle.setSpeed(speed)
            elif -Circle.getR() <= distance <= 0:
                posPP = posP+(posAa-posP)*disBbP/(disAaP+disBbP)+(posBb-posP)*disAaP/(disAaP+disBbP) - rotateAB/disAB*Circle.getR()*1.05
                speed = speedP-rotateAB*np.cross(posB-posA,speedP)*(1+elastic)/np.dot(posB-posA,posB-posA)
                Circle.setPos(posPP)
                Circle.setSpeed(speed)
                Circle.empower(rotateAB/disAB*massP*np.linalg.norm(speedP-speed)*5)
    def collisionCircleXCircle(self,CircleA,CircleB):
        posA = CircleA.getPos()
        posB = CircleB.getPos()
        speedA = CircleA.getSpeed()
        speedAnorm = np.linalg.norm(speedA)
        speedB = CircleB.getSpeed()
        speedBnorm = np.linalg.norm(speedB)
        massA = CircleA.getMass()
        massB = CircleB.getMass()
        disAB = np.linalg.norm(posB-posA)
        rotateAB = np.dot(posB-posA,np.array([[0,1],[-1,0]]))
        if disAB <= CircleA.getR() + CircleB.getR():
            print('Collision!!')
            speedAa = (massA*speedA+massB*speedB - elastic*massB*(speedA-speedB)) / (massA+massB)
            speedBb = (massA*speedA+massB*speedB - elastic*massA*(speedB-speedA)) / (massA+massB)
            CircleA.setSpeed(speedAa)
            CircleB.setSpeed(speedBb)
            CircleA.setPos(posA + (posA-posB)*0.01)
            CircleB.setPos(posB + (posB-posA)*0.01)
            CircleA.empower((posA-posB)/disAB*massA*np.linalg.norm(speedAa-speedA)*5)
            CircleB.empower((posB-posA)/disAB*massB*np.linalg.norm(speedBb-speedB)*5)
    def calc(self,deltaTime):
        CircleObjects = self.getFreeCircleObjects()
        for i in range(len(CircleObjects)):
            CircleObject = CircleObjects[i]
            CircleObject.empower(gravity*CircleObject.getMass())
            for LineObject in self.getFixedLineObjects():
                self.collisionCircleXLine(CircleObject,LineObject)
            for j in range(len(CircleObjects)-i-1):
                CircleObject2 = CircleObjects[i+j+1]
                self.collisionCircleXCircle(CircleObject,CircleObject2)
            CircleObject.reflect(deltaTime)
                
offsetX,offsetY = 400,470
dropLineLength,dropLineY = 400,440
FruitsColor = [(255,197,197),(255,197,220),(230,197,255),(255,227,197),(255,218,197),(255,197,207),
               (249,255,197),(255,197,232),(255,253,197),(232,255,197),(200,255,197)]
class SuikaEngine(PhysicsEngine):
    def __init__(self):
        super().__init__()
        self.preFruitID = 6
        self.createBascket()
        self.world = b2.world(gravity=(0, -10), doSleep=True)
        self.falling_body = self.world.CreateDynamicBody(position=(0, 15), shapes=b2.polygonShape(box=(1, 1)))
        self.play()
    def createFruit(self,mouseX,mouseY):
        fruitID = self.preFruitID
        pos= {'X':mouseX,'Y':dropLineY,'R':fruitID*5+10}
        self.objects.append(FruitCircle(type='Circle',isFixed=False,mass=1,pos=pos,fruitID=fruitID))
        self.preFruitID = random.randint(1,5)
    def createBascket(self):
        self.createLine(isFixed=True,pos={'X1':200,'Y1':400,'X2':200,'Y2':0})
        self.createLine(isFixed=True,pos={'X1':-200,'Y1':400,'X2':-200,'Y2':0})
        self.createLine(isFixed=True,pos={'X1':200,'Y1':0,'X2':-200,'Y2':0})
        #self.createLine(isFixed=True,pos={'X1':-200,'Y1':0,'X2':200,'Y2':0})
    def render(self,screen,mouseX,mouseY):
        for Line in self.getFixedLineObjects():
            pygame.draw.line(screen, (255,219,90),
                (offsetX+Line.getX1(),offsetY-Line.getY1()),
                (offsetX+Line.getX2(),offsetY-Line.getY2()),1)
            pygame.draw.circle(screen,(255,219,90),(offsetX+Line.getX1()+1,offsetY-Line.getY1()+1),1)
            pygame.draw.circle(screen,(255,219,90),(offsetX+Line.getX2()+1,offsetY-Line.getY2()+1),1)
        for Fruit in self.getFreeCircleObjects():
            pygame.draw.circle(screen,FruitsColor[Fruit.getFruitID()],(offsetX+Fruit.getX()+1,offsetY-Fruit.getY()),Fruit.getR())
        pygame.draw.line(screen, (255,247,219),
            (offsetX+mouseX,offsetY-dropLineY),
            (offsetX+mouseX,offsetY-0),4)
        pygame.draw.circle(screen,(255,255,255),(offsetX+mouseX,offsetY-dropLineY),20)
        return screen
    def play(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 500))
        preTime = time.time()
        while True:
            mouseX, mouseY = pygame.mouse.get_pos()
            mouseX, mouseY = mouseX-offsetX, mouseY-offsetY
            self.world.Step(1/60, 10, 8)
            if mouseX < -dropLineLength/2:
                mouseX = -dropLineLength/2
            elif dropLineLength/2 < mouseX:
                mouseX = dropLineLength/2
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    self.createFruit(mouseX,mouseY)
            deltaTime = preTime - time.time()
            preTime = time.time()
            self.calc(deltaTime)
            screen.fill((255,243,200))
            screen = self.render(screen,mouseX,mouseY)
            pygame.display.update()
            time.sleep(1/100)
            

if __name__ == "__main__":
    SuikaEngine()