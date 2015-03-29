# Maze written using pygame

import sys, pygame, time
from PmzGraphics import *

# Action states
S_init=-1
S_none=0
S_right=1
S_left=2
S_up=3
S_down=4

class DrawTask:
    def __init__(self, sprite, x, y):
        self.sprite = sprite
        self.x = x
        self.y = y

    def apply(self, screen):
        screen.blit(self.sprite.img, self.sprite.rect.move(self.x, self.y))


class UndrawTask:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def apply(self, screen, bgScreen):
        try:
            bgImg = bgScreen.subsurface(pygame.Rect(self.x, self.y, self.w, self.h))
            screen.blit(bgImg, pygame.Rect(self.x, self.y, bgImg.get_rect().width, bgImg.get_rect().height))
        except ValueError as e:
            print('Failed with',e,'with',self.x,self.y,self.w,self.h)
        

class RedrawsRequired:
    def __init__(self):
        self.reset()

    def reset(self):
        self.bgRedraws = []
        self.fgRedraws = []

    def addFg(self, task):
        self.fgRedraws.append(task)

    def addBg(self, task):
        self.bgRedraws.append(task)

    def apply(self, screen, bgScreen):
        for x in self.bgRedraws: x.apply(screen, bgScreen)
        for x in self.fgRedraws: x.apply(screen)
        self.reset()
        

class Player():
    def __init__(self, sprite, xpos, ypos):
        self.sprite = sprite
        self.xpos = xpos
        self.ypos = ypos
        self.xoff = 0
        self.yoff = 0
        self.w = sprite.w
        self.h = sprite.h
        print('Got h of',self.h)
        self.action = S_none

    def animate(self, rr):
        if self.action == S_right:
            rr.addBg(UndrawTask(self.makeX(), self.makeY(), 50, self.h))
            self.xoff += 5
        elif self.action == S_left:
            rr.addBg(UndrawTask(self.makeX()+self.w-50, self.makeY(), 50, self.h))
            self.xoff -= 5
        elif self.action == S_up:
            rr.addBg(UndrawTask(self.makeX(), self.makeY()+self.h*0.4, self.w, self.h*0.6))
            self.yoff -= 4
        elif self.action == S_down:
            rr.addBg(UndrawTask(self.makeX(), self.makeY(), self.w, self.h*0.66))
            self.yoff += 4
        self.draw(rr)

    def draw(self, rr):
        rr.addFg(DrawTask(self.sprite, self.makeX(), self.makeY()))

    def makeX(self): return self.xpos*100+self.xoff
                 
    def makeY(self): return self.ypos*80+self.yoff-40

    def move(self):
        if self.action == S_right: self.xpos += 1
        elif self.action == S_left: self.xpos -= 1
        elif self.action == S_up: self.ypos -= 1
        elif self.action == S_down: self.ypos += 1
        self.action = S_none
        self.xoff = 0
        self.yoff = 0
        


class Room:
    def __init__(self, definitionGridFile):
        lines = [x.rstrip() for x in open(definitionGridFile).readlines()]
        w = 9
        h = 8
        self.tiles = [[0 for x in range(h)] for x in range(w)] 
        self.description = lines[0]
        for y in range(h):
            line = lines[2+y]
            for x in range(w):
                tile = line[1+x]
                self.tiles[x][y] = tile

class World:
    pass

# WorldChangeActions:
#  MovePlayer(player, direction)
#  TransportPlayer(player, newPos)
#  UpdateFloorAt(pos, floorId)
#  UpdateItemAt(pos, itemId)
#  AddPlayerInventory(player, itemId)
#  RemovePlayerInventory(player, itemId)
#  UpdateMsgForPlayer(player, message)
#  PlayerWins(player)
#  SetPlayerHealth(player, level)

class GameController:
    def onInitWorld(self, world): pass

    def onPlayerMoveRequested(self, world, player, reqAction): pass

    # e.g. handle commands like get, combine
    def onPlayerCommand(self, world, player, command): pass

    # List[worldChanges]
    def onGameTimePasses(self, world, gameTime): pass

    def onAnimationTick(self, world, gameTime, gameTick): pass

    def onPlayerTalks(self, world, player, message): pass

    def onPlayerJoin(self, world, player): pass
    

print("Got here")

def playGame(gameCtrl):
    try:
        gameTime = 0
        pygame.init()
        size = width, height = 1024, 800
        screen = pygame.display.set_mode(size)
        bgScreen = screen.copy()

        backgrounds = Backgrounds('backgrounds.txt')
        world = World()
        room = Room("rooms.txt")

        girlPrincess = Player(Sprite("images/Character Princess Girl.png"), 1, 1)
        boy = Player(Sprite("images/Character Boy.png"), 1, 3)

        gameCtrl.onInitWorld(world)
        drawBackground(screen, backgrounds, room)
        drawBackground(bgScreen, backgrounds, room)

        pygame.display.flip()
        move=S_init
        while 1:
            gameCtrl.onGameTimePasses(world, gameTime)
            if move != S_none:
                girlPrincess.action = move
                boy.action = move
                
                for aniStep in range(0,20):
                    rr = RedrawsRequired()
                    gameCtrl.onAnimationTick(world, gameTime, aniStep)
                    girlPrincess.animate(rr)
                    boy.animate(rr)
                    rr.apply(screen, bgScreen)
                    #drawBackground(screen)
                    pygame.display.flip()
                    time.sleep(0.01)
                
                girlPrincess.move()
                boy.move()
                drawBackground(screen, backgrounds, room)
                girlPrincess.draw(rr)
                boy.draw(rr)
                rr.apply(screen, bgScreen)
                pygame.display.flip()
                move = S_none

            elif move == S_none:
                for event in pygame.event.get():
                    et = event.type
                    if et == pygame.QUIT or (et == pygame.KEYDOWN and event.key == pygame.K_q): sys.exit()
                    if et == pygame.KEYDOWN:
                        k = event.key
                        if k == pygame.K_x: move=S_right
                        elif k == pygame.K_z: move=S_left
                        elif k == pygame.K_k: move=S_up
                        elif k == pygame.K_m: move=S_down

    finally:
        pygame.quit()
        print("Exit")

gameCtrl = GameController()

playGame(gameCtrl)
