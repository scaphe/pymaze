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
    def __init__(self, filename):
        self.Width = 100
        self.Height = 80
        # Halve size of sprites
        self.Width = 50
        self.Height = 40
        self.name = os.path.basename(filename)
        self.filename = filename
        self.img = pygame.image.load(filename).convert_alpha()
        self.img = pygame.transform.smoothscale(self.img, (int(self.img.get_rect().width/2), int(self.img.get_rect().height/2)))
        rect = self.img.get_rect()
        self.width = rect.width
        self.height = rect.height

    def drawAt(self, screen, x, y, xoff, yoff):
        screen.blit(self.img, (self.xOf(x, xoff), self.yOf(y, yoff)))

    def xOf(self, x, xoff):
        return int((x+xoff/100) * self.Width)

    def yOf(self, y, yoff):
        return int((y+yoff/100) * self.Height)


class Backgrounds:
    def __init__(self, backgroundMapFile):
        self.map = {}
        for aline in open(backgroundMapFile):
            line = aline.rstrip()
            if line != '':
                tileId = line[0]
                self.map[tileId] = Sprite(line[2:])
                #print("Set tileId '"+str(tileId)+"' is",self.map[tileId].filename)

    def getSprite(self, id):
        return self.map[id]


# Keep track of wanting to draw a sprite at a place on the screen
class DrawTask:
    def __init__(self, sprite, pos, xoff, yoff):
        self.sprite = sprite
        self.pos = pos
        self.xoff = xoff
        self.yoff = yoff

    def apply(self, screen):
        self.sprite.drawAt(screen, self.pos.x(), self.pos.y(), self.xoff, self.yoff)


# Keep track of wanting to undraw a rectangle on the screen
class UndrawTask:
    def __init__(self, sprite, pos):
        self.sprite = sprite
        self.pos = pos

    def apply(self, screen, bgScreen):
        try:
            x = self.sprite.xOf(self.pos.x(), 0)
            y = self.sprite.yOf(self.pos.y(), 0)
            bgImg = bgScreen.subsurface(pygame.Rect(x, y, self.sprite.width, self.sprite.height))
            screen.blit(bgImg, pygame.Rect(x, y, bgImg.get_rect().width, bgImg.get_rect().height))
        except ValueError as e:
            print('Failed with',e,'with',self.x,self.y,self.w,self.h)
        

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
            screen.blit(img, pygame.Rect(self.x, currY, r.width, r.height))
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
    def __init__(self):
        size = 1224, 800
        self.screen = pygame.display.set_mode(size)

    def setBackgrounds(self, backgrounds):
        self.backgrounds = backgrounds

    def setCurrentRoom(self, room):
        self._currentRoom = room
        # Init bgScreen so we can undraw stuff
        self.bgScreen = self.screen.copy()
        self.drawBackground(self.bgScreen, room)

    def drawRoom(self):
        self.drawBackground(self.screen, self._currentRoom)
        pygame.display.flip()

    def drawUpdates(self, rr):
        rr.apply(self.screen, self.bgScreen)
        pygame.display.flip()

    def drawBackground(self, screen, room):
        black = 90, 90, 90
        screen.fill(black)
        for x in range(0, 11):
            for y in range(0, 8):
                tile = room.tiles[x][y]
                if tile != ' ':
                    bg = self.backgrounds.map[tile]
                    bg.drawAt(screen, x, y, 0, 0)

