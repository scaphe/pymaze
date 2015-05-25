# Maze written using pygame

import sys, pygame, time, json, pprint
import queue

from PmzGraphics import *
from GameController import *
from Player import *
from GameHost import *


# Contains definition of room
# self.tiles - 2x2 array of sprite ids
class Room:
    def __init__(self, roomDef):
        self.id = roomDef['roomId']
        self.name = roomDef['name']
        w = 11
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
class WorldState:
    def __init__(self, screen, worldDefFile):
        self.screen = screen
        with open(worldDefFile) as f:
            self.worldDef = json.load(f)
            pprint.pprint(self.worldDef)
        w = self.worldDef
        self.worldName = w['world']
        self.rooms = [Room(roomDef) for roomDef in w['rooms']]
        self.players = []
        self._localPlayer = None

    def addPlayer(self, p):
        self.players.append(p)
        return p

    def setLocalPlayer(self, player):
        self._localPlayer = player
        if self.screen is not None:
            self.screen.setCurrentRoom(self._localPlayer._currentRoom)

    def updatePlayers(self, rr):
        for p in self.players: p.update(self, rr)
        if rr.redrawPlayers:
            for p in self.players: p.draw(rr)

    def isFreeSpace(self, room, pos):
        if room.tiles[pos.x()][pos.y()] == ' ' and not self.isPlayerAt(room, pos): return True
        else: return False

    def isPlayerAt(self, room, pos):
        return (len([p for p in self.players if p._pos.equals(pos)]) > 0)

    def playersReactToKey(self, gameCtrl, key):
        for player in self.players:
            moveAction = player.actionFromKey(key)
            # Apply any user actions
            if moveAction != Action.NONE:
                print('Player',player,'taking action of',moveAction)
                gameCtrl.onPlayerMoveRequested(self, player, moveAction)

    def processQueuedActions(self, gameQueue):
        while not gameQueue.empty():
            ev = gameQueue.get()
            player = next((x for x in self.players if x.playerId == ev.playerId), None)
            player.takeAction(ev.actionType)


def playGame(gameCtrl):
    try:
        gameTime = 0

        pygame.init()

        screen = Screen()
        backgrounds = Backgrounds('resources/backgrounds.txt')
        screen.setBackgrounds(backgrounds)
        gameHost = GameHost()
        world = WorldState(screen, "resources/rooms.txt")
        room = world.rooms[0]

        boy = world.addPlayer(Player(0, backgrounds.getSprite('0'), room, 1, 1))
        world.addPlayer(Player(1, backgrounds.getSprite('1'), room, 1, 3))
        world.addPlayer(Player(2, backgrounds.getSprite('2'), room, 4, 3))
        world.addPlayer(Player(3, backgrounds.getSprite('3'), room, 5, 3))
        player = boy

        gameCtrl.onInitWorld(world)

        world.setLocalPlayer(boy)
        screen.drawRoom()

        while 1:
            gameCtrl.onGameTimePasses(world, gameTime)

            # Drain event queue and check for user actions
            moveAction = Action.NONE
            for event in pygame.event.get():
                et = event.type
                if et == pygame.QUIT or (et == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): sys.exit()
                if et == pygame.KEYDOWN:
                    world.playersReactToKey(gameCtrl, event.key)

            world.processQueuedActions(gameCtrl.gameQueue)

            # Redraw screen, moving players around as required
            rr = RedrawsRequired()
            world.updatePlayers(rr)
            rr.addFg(DrawTextTask("hi dave\nwith a newline", 16,4))

            screen.drawUpdates(rr)

            time.sleep(0.01)

    finally:
        pygame.quit()
        print("Exit")

# Actually run the game
gameQueue = queue.Queue()
gameController = GameController()
gameCtrl = LocalGameController(gameQueue, gameController)
playGame(gameCtrl)
