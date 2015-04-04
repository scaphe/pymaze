# Maze written using pygame

import sys, pygame, time, json, pprint


from PmzGraphics import *
from GameController import *


# Immutable (nice callers respecting my underscores) position
class Pos:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __str__(self): return "Pos("+str(self._x)+", "+str(self._y)+")"

    def x(self): return self._x
    def y(self): return self._y

    # Returns a changed copy
    def plus(self, other):
        return Pos(self._x + other._x, self._y + other._y)

    def isEmpty(self): return self._x == 0 and self._y == 0


# Action states
class Action:
    INIT = -1
    NONE = 0
    MOVE_RIGHT = 1
    MOVE_LEFT = 2
    MOVE_UP = 3
    MOVE_DOWN = 4

    def __init__(self):
        pass


class Player():
    def __init__(self, sprite, xpos, ypos):
        self._animating = 0
        self.sprite = sprite
        self._needDraw = True
        self._pos = Pos(xpos, ypos)
        self.xpos = xpos
        self.ypos = ypos
        self.xoff = 0
        self.yoff = 0
        self.w = sprite.w
        self.h = sprite.h
        print('Got h of',self.h)

    def isBusy(self):
        self.animating = 0

    def takeAction(self, action):
        if action == Action.MOVE_RIGHT: self._aniDelta = Pos(1, 0)
        elif action == Action.MOVE_LEFT: self._aniDelta = Pos(-1, 0)
        elif action == Action.MOVE_UP: self._aniDelta = Pos(0, -1)
        elif action == Action.MOVE_DOWN: self._aniDelta = Pos(0, 1)
        else: self._aniDelta = Pos(0, 0)

        if not self._aniDelta.isEmpty():
            print('Starting move using ', self._aniDelta,'from action of',action)
            # We are going to animate from the current position to the new position
            self._animating = 20
            self._aniAction = action
            self._needDraw = True
            self._aniPos = self._pos
            self._pos = self._pos.plus(self._aniDelta)
            self.xoff = 0
            self.yoff = 0
        else:
            print('No move cos',action,' so using', self._aniDelta)

    def animate(self, rr):
        if self._aniAction == Action.MOVE_RIGHT:
            rr.addBg(UndrawTask(self.makeX(self._aniPos), self.makeY(self._aniPos), 50, self.h))
            self.xoff += 5
        elif self._aniAction == Action.MOVE_LEFT:
            rr.addBg(UndrawTask(self.makeX(self._aniPos)+self.w-50, self.makeY(self._aniPos), 50, self.h))
            self.xoff -= 5
        elif self._aniAction == Action.MOVE_UP:
            rr.addBg(UndrawTask(self.makeX(self._aniPos), self.makeY(self._aniPos)+self.h*0.4, self.w, self.h*0.6))
            self.yoff -= 4
        elif self._aniAction == Action.MOVE_DOWN:
            rr.addBg(UndrawTask(self.makeX(self._aniPos), self.makeY(self._aniPos), self.w, self.h*0.66))
            self.yoff += 4
        rr.addFg(DrawTask(self.sprite, self.makeX(self._aniPos), self.makeY(self._aniPos)))

    def update(self, rr):
        if self._animating > 0:
            self._animating -= 1
            self.animate(rr)
        else:
            if self._needDraw:
                self.xoff = 0
                self.yoff = 0
                print('Drawing at',self._pos)
                rr.addFg(DrawTask(self.sprite, self.makeX(self._pos), self.makeY(self._pos)))
                self._needDraw = False

    def makeX(self, pos): return pos.x() * 100  + self.xoff
                 
    def makeY(self, pos): return pos.y() * 80   + self.yoff-40
        
    def actionFromKey(self, k):
        if k == pygame.K_x: return Action.MOVE_RIGHT
        elif k == pygame.K_z: return Action.MOVE_LEFT
        elif k == pygame.K_k: return Action.MOVE_UP
        elif k == pygame.K_m: return Action.MOVE_DOWN
        else: return Action.NONE



class Room:
    def __init__(self, roomDef):
        self.id = roomDef['roomId']
        self.name = roomDef['name']
        w = 9
        h = 8
        self.tiles = [[0 for x in range(h)] for x in range(w)] 
        lines = roomDef['rows']
        self.description = lines[0]
        for y in range(h):
            line = lines[1+y]
            for x in range(w):
                tile = line[1+x]
                self.tiles[x][y] = tile


# State of the World, this keeps track of everything
class World:
    def __init__(self, screen, worldDefFile, backgroundsFile):
        self.screen = screen
        self.backgrounds = Backgrounds(backgroundsFile)

        with open(worldDefFile) as f:
            self.worldDef = json.load(f)
            pprint.pprint(self.worldDef)
        w = self.worldDef
        self.worldName = w['world']
        self.rooms = [Room(roomDef) for roomDef in w['rooms']]
        self.players = []

    def setCurrentRoom(self, room):
        self._currentRoom = room
        # Init bgScreen so we can undraw stuff
        self.bgScreen = self.screen.copy()
        drawBackground(self.bgScreen, self.backgrounds, room)

    def addPlayer(self, p):
        self.players.append(p)

    def updatePlayers(self, rr):
        for p in self.players: p.update(rr)

    def drawRoom(self):
        drawBackground(self.screen, self.backgrounds, self._currentRoom)
        pygame.display.flip()

    def drawUpdates(self, rr):
        rr.apply(self.screen, self.bgScreen)
        pygame.display.flip()



def playGame(gameCtrl):
    try:
        gameTime = 0
        size = width, height = 1024, 800

        pygame.init()
        screen = pygame.display.set_mode(size)

        world = World(screen, "rooms.txt", 'backgrounds.txt')
        room = world.rooms[0]

        girlPrincess = Player(Sprite("images/Character Princess Girl.png"), 1, 1)
        boy = Player(Sprite("images/Character Boy.png"), 1, 3)
        world.addPlayer(girlPrincess)
        world.addPlayer(boy)
        player = boy

        gameCtrl.onInitWorld(world)

        world.setCurrentRoom(room)
        world.drawRoom()

        while 1:
            gameCtrl.onGameTimePasses(world, gameTime)

            # Drain event queue and check for user actions
            moveAction = Action.NONE
            for event in pygame.event.get():
                et = event.type
                if et == pygame.QUIT or (et == pygame.KEYDOWN and event.key == pygame.K_q): sys.exit()
                if et == pygame.KEYDOWN:
                    if not player.isBusy():
                        moveAction = player.actionFromKey(event.key)

            # Apply any user actions
            if moveAction != Action.NONE:
                print('Taking action of ',moveAction)
                moveAction = gameCtrl.onPlayerMoveRequested(world, player, moveAction)
                player.takeAction(moveAction)
                
            # Redraw screen, moving players around as required
            rr = RedrawsRequired()
            world.updatePlayers(rr)
            world.drawUpdates(rr)

            time.sleep(0.01)

    finally:
        pygame.quit()
        print("Exit")

# Actually run the game
gameCtrl = GameController()
playGame(gameCtrl)
