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
    def __init__(self, worldDefFile):
        with open(worldDefFile) as f:
            self.worldDef = json.load(f)
            pprint.pprint(self.worldDef)
        w = self.worldDef
        self.worldName = w['world']
        self.rooms = [Room(roomDef) for roomDef in w['rooms']]
        self.players = []

    def addPlayer(self, p):
        self.players.append(p)
        return p

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


class GameRunner:
    def run(self, screen, world, player):
        self.screen = screen
        self.screen.loadSprites('resources/backgrounds.txt')
        self.gameHost = GameHost()
        self.world = world

        self.screen.setCurrentRoom(player._currentRoom)
        self.screen.drawRoom()

    def runLoop(self):
        # Redraw screen, moving players around as required
        rr = RedrawsRequired()
        self.world.updatePlayers(rr)
        rr.addFg(DrawTextTask("hi dave\nwith a newline", 16,4))

        self.screen.drawUpdates(rr)


class Main:
    def playGame(self, gameCtrl):
        try:
            pygame.init()

            size = 1224, 800
            pyScreen = pygame.display.set_mode(size)

            # Setup world state
            world = WorldState("resources/rooms.txt")
            room = world.rooms[0]
            player1 = world.addPlayer(Player(0, '0', room, 1, 1))
            player2 = world.addPlayer(Player(1, '1', room, 1, 3))
            world.addPlayer(Player(2, '2', room, 4, 3))
            world.addPlayer(Player(3, '3', room, 5, 3))

            # Setup two screens/games
            black = 90, 90, 90
            screen1 = Screen(TransposedPyScreen(pyScreen, 4, 50, 0.5, 0.5), black)
            game1 = GameRunner()
            game1.run(screen1, world, player1)

            black2 = 128,0,0
            screen2 = Screen(TransposedPyScreen(pyScreen, 580, 50, 0.5, 0.5), black2)
            game2 = GameRunner()
            game2.run(screen2, world, player2)

            pygame.display.flip()

            # Main game loop, on local machine, reading keys etc
            gameTime = 0
            gameCtrl.onInitWorld(world)

            while 1:
                gameTime = gameTime + 1
                gameCtrl.onGameTimePasses(world, gameTime)

                # Drain event queue and check for user actions
                for event in pygame.event.get():
                    et = event.type
                    if et == pygame.QUIT or (et == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): sys.exit()
                    if et == pygame.KEYDOWN:
                        world.playersReactToKey(gameCtrl, event.key)

                world.processQueuedActions(gameCtrl.gameQueue)

                game1.runLoop()
                game2.runLoop()
                pygame.display.flip()

                time.sleep(0.01)

        finally:
            pygame.quit()
            print("Exit")

    def run(self):
        # Actually run the game
        gameQueue = queue.Queue()
        gameController = GameController()
        gameCtrl = LocalGameController(gameQueue, gameController)
        self.playGame(gameCtrl)

Main().run()
