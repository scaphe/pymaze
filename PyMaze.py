# Maze written using pygame

import sys, pygame, time, json, pprint
import queue

from PmzGraphics import *
from GameController import *
from Player import *



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
        self._currentRoom = None

    def setCurrentRoom(self, room):
        self._currentRoom = room
        # Init bgScreen so we can undraw stuff
        self.bgScreen = self.screen.copy()
        drawBackground(self.bgScreen, self.backgrounds, room)

    def addPlayer(self, p):
        self.players.append(p)

    def isFreeSpace(self, room, pos):
        if room.tiles[pos.x()][pos.y()] == ' ' and not self.isPlayerAt(room, pos): return True
        else: return False

    def isPlayerAt(self, room, pos):
        return (len([p for p in self.players if p._pos.equals(pos)]) > 0)

    def updatePlayers(self, rr):
        for p in self.players: p.update(self, rr)

    def drawRoom(self):
        drawBackground(self.screen, self.backgrounds, self._currentRoom)
        pygame.display.flip()

    def drawUpdates(self, rr):
        rr.apply(self.screen, self.bgScreen)
        pygame.display.flip()

    def processQueuedActions(self, gameQueue):
        while not gameQueue.empty():
            ev = gameQueue.get()
            player = next((x for x in self.players if x.playerId == ev.playerId), None)
            player.takeAction(ev.actionType)


def playGame(gameCtrl):
    try:
        gameTime = 0
        size = width, height = 1024, 800

        pygame.init()
        screen = pygame.display.set_mode(size)

        world = World(screen, "rooms.txt", 'backgrounds.txt')
        room = world.rooms[0]

        girlPrincess = Player(1, False, Sprite("images/Character Princess Girl.png"), 1, 1)
        boy = Player(2, True, Sprite("images/Character Boy.png"), 1, 3)
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
                    moveAction = player.actionFromKey(event.key)

            # Apply any user actions
            if moveAction != Action.NONE:
                print('Taking action of ',moveAction)
                moveAction = gameCtrl.onPlayerMoveRequested(world, player, moveAction)

            world.processQueuedActions(gameCtrl.gameQueue)

            # Redraw screen, moving players around as required
            rr = RedrawsRequired()
            world.updatePlayers(rr)
            world.drawUpdates(rr)

            time.sleep(0.01)

    finally:
        pygame.quit()
        print("Exit")

# Actually run the game
gameQueue = queue.Queue()
gameCtrl = LocalGameController(gameQueue, GameController())
playGame(gameCtrl)
