import sys, pygame, time, os


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

    def equals(self, other):
        if self._x == other._x and self._y == other._y: return True
        else: return False

    def isEmpty(self): return self._x == 0 and self._y == 0


class Sprite():
    # xoff and yoff are in percent
    def __init__(self, filename, screen):
        self.name = os.path.basename(filename)
        self.filename = filename
        self.img = pygame.image.load(filename).convert_alpha()
        rect = self.img.get_rect()
        self.width = rect.width
        self.height = rect.height
        # Sprites are too tall, cos they have the top transparent bit at the moment, so fix the height
        self.width = 100
        self.height = 80
        # Scale what we are going to draw on the screen, screen will scale all coords we draw at
        self.img = pygame.transform.smoothscale(self.img, (
            int(self.img.get_rect().width * screen.scaleX), 
            int(self.img.get_rect().height * screen.scaleY)))
        print('Got sprite w/h of ',self.width,'/',self.height)

    def drawAt(self, pyScreen, x, y, xoff, yoff):
        pyScreen.blit(self.img, (self.xOf(x, xoff), self.yOf(y, yoff)))

    def xOf(self, x, xoff):
        return int((x+xoff/100) * self.width)

    def yOf(self, y, yoff):
        return int((y+yoff/100) * self.height)


class SpriteStore:
    def __init__(self, spritesMapFile, screen):
        self.map = {}
        for aline in open(spritesMapFile):
            line = aline.rstrip()
            if line != '':
                tileId = line[0]
                sprite = Sprite(line[2:], screen)
                self.map[tileId] = sprite
                self.width = sprite.width
                self.height = sprite.height
                #print("Set tileId '"+str(tileId)+"' is",self.map[tileId].filename)

    def getSprite(self, id):
        return self.map[id]


# Keep track of wanting to draw a sprite at a place on the screen
class DrawTask:
    def __init__(self, spriteId, pos, xoff, yoff):
        self.spriteId = spriteId
        self.pos = pos
        self.xoff = xoff
        self.yoff = yoff

    def apply(self, screen):
        sprite = screen.findSprite(self.spriteId)
        sprite.drawAt(screen.pyScreen, self.pos.x(), self.pos.y(), self.xoff, self.yoff)


# Keep track of wanting to undraw a rectangle on the screen
class UndrawTask:
    def __init__(self, spriteId, pos):
        self.spriteId = spriteId
        self.pos = pos

    def apply(self, screen, bgScreen):
        try:
            sprite = screen.findSprite(self.spriteId)
            x = sprite.xOf(self.pos.x(), 0)
            y = sprite.yOf(self.pos.y(), 0)
            bgImg = bgScreen.subsurface(pygame.Rect(x, y, sprite.width, sprite.height))
            screen.pyScreen.blit(bgImg, pygame.Rect(x, y, bgImg.get_rect().width, bgImg.get_rect().height))
        except ValueError as e:
            print('Failed with',e,'with',self.spriteId,self.pos.x(),self.pos.y())
        

class DrawTextTask:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def apply(self, screen):
        f = pygame.font.SysFont("monospace", 20)
        currY = self.y
        for line in self.text.split("\n"):
            img = f.render(line, 0, (255, 0, 0))
            r = img.get_rect()
            screen.pyScreen.blit(img, pygame.Rect(self.x, currY, r.width, r.height))
            currY += r.height


# Keep track of what redraws we want to do, apply() will actually draw them (in the right order)
class RedrawsRequired:
    def __init__(self):
        self.reset()

    def reset(self):
        self.bgRedraws = []
        self.fgRedraws = []
        self.redrawPlayers = False

    def addFg(self, task):
        self.fgRedraws.append(task)

    def addBg(self, task):
        self.bgRedraws.append(task)

    def apply(self, screen, bgScreen):
        for x in self.bgRedraws: x.apply(screen, bgScreen)
        for x in self.fgRedraws: x.apply(screen)
        self.reset()
        

class Screen:
    def __init__(self, pyScreen, black):
        self.pyScreen = pyScreen
        self.black = black

    def loadSprites(self, spritesMapFile):
        self.spriteStore = SpriteStore(spritesMapFile, self.pyScreen)
        self.pyScreen.setSize(11*self.spriteStore.width, 8*self.spriteStore.height)
        return self.spriteStore

    def findSprite(self, spriteId):
        return self.spriteStore.map[spriteId]

    def setCurrentRoom(self, room):
        self._currentRoom = room
        # Init bgScreen so we can undraw stuff
        self.bgPyScreen = self.pyScreen.copy()
        self.drawBackground(self.bgPyScreen, room)

    def drawRoom(self):
        self.drawBackground(self.pyScreen, self._currentRoom)

    def drawUpdates(self, rr):
        rr.apply(self, self.bgPyScreen)

    def drawBackground(self, pyScreen, room):
        pyScreen.fill(self.black)
        for x in range(0, 11):
            for y in range(0, 8):
                tile = room.tiles[x][y]
                if tile != ' ':
                    bg = self.spriteStore.map[tile]
                    bg.drawAt(pyScreen, x, y, 0, 0)


class TransposedPyScreen:
    def __init__(self, pyScreen, offsetX, offsetY, scaleX, scaleY, maxX=100, maxY=150):
        self.pyScreen = pyScreen
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.scaleX = scaleX
        self.scaleY = scaleY
        self.maxX = maxX
        self.maxY = maxY

    def setSize(self, szX, szY):
        self.maxX = self.offsetX + (szX * self.scaleX)
        self.maxY = self.offsetY + (szY * self.scaleY)

    def shiftX(self, x): return (x * self.scaleX) + self.offsetX

    def shiftY(self, y): return (y * self.scaleY) + self.offsetY

    def blit(self, img, xy):
        x = xy[0]
        y = xy[1]
        x = self.shiftX(x)
        y = self.shiftY(y)
        try:
            w = xy[2] * self.scaleX
            h = xy[3] * self.scaleY
            self.pyScreen.blit(img, pygame.Rect(x, y, w, h))
        except:
            self.pyScreen.blit(img, (x, y))

    def subsurface(self, r):
        x = self.shiftX(r.x)
        y = self.shiftY(r.y)
        ss = pygame.Rect(x, y, r.w, r.h)
        return self.pyScreen.subsurface(ss)

    def fill(self, colour):
        self.pyScreen.fill(colour, pygame.Rect(self.offsetX, self.offsetY, self.maxX, self.maxY))

    def copy(self):
        return TransposedPyScreen(self.pyScreen.copy(), self.offsetX, self.offsetY, self.scaleX, self.scaleY, self.maxX, self.maxY)
