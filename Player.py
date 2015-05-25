
from PmzGraphics import *
from GameController import *
from KeySet import *


class Player():
    def __init__(self, playerId, sprite, room, xpos, ypos):
        self.keySet = Constants.keySets[playerId]
        self.playerId = playerId
        self._currentRoom = room
        self.sprite = sprite
        self._pos = Pos(xpos, ypos)
        # How many steps of animation are remaining
        self.NumberOfAnimationSteps = 20
        self._animating = 0
        # _aniPos is the previous position that we are animating from
        self._aniPos = None
        # _xoff/_yoff is how far along the animation we are, in percent
        self._xoff = 0
        self._yoff = 0
        #self.w = sprite.w
        #   self.h = sprite.h
        self._pendingAction = Action.NONE
        self._wantRedraw = True
        #print('Got h of',self.h)

    def __str__(self):
        return "Player("+str(self.playerId)+", sprite='"+self.sprite.name+"', pos="+str(self._pos)+")"

    def isBusy(self):
        return self._animating != 0

    def takeAction(self, action):
        print('takeAction called with',action)
        self._pendingAction = action

    def draw(self, rr):
        if self._animating > 0:
            rr.addBg(UndrawTask(self.sprite, self._aniPos))
            rr.addBg(UndrawTask(self.sprite, self._pos))
            rr.addFg(DrawTask(self.sprite, self._aniPos, self._xoff, self._yoff))
        else:
            #print('Drawing',self.playerId,'at',self._pos,'with offsets',self._xoff,',',self._yoff)
            rr.addBg(UndrawTask(self.sprite, self._pos))
            rr.addFg(DrawTask(self.sprite, self._pos, 0, 0))

    def _animate(self, rr):
        undrawRequired = False
        aniStep = 100 / self.NumberOfAnimationSteps
        if self._aniAction == Action.MOVE_RIGHT:
            undrawRequired = True
            self._xoff += aniStep
        elif self._aniAction == Action.MOVE_LEFT:
            undrawRequired = True
            self._xoff -= aniStep
        elif self._aniAction == Action.MOVE_UP:
            undrawRequired = True
            self._yoff -= aniStep
        elif self._aniAction == Action.MOVE_DOWN:
            undrawRequired = True
            self._yoff += aniStep
        if undrawRequired:
            rr.addBg(UndrawTask(self.sprite, self._aniPos))
            rr.addBg(UndrawTask(self.sprite, self._pos))
        rr.redrawPlayers = True
        #rr.addFg(DrawTask(self.sprite, self._makeX(self._aniPos), self._makeY(self._aniPos)))

    def update(self, world, rr):
        if self._animating > 0:
            self._animating -= 1
            self._animate(rr)
            if self._animating == 0:
                self._xoff = 0
                self._yoff = 0
        else:
            if self._wantRedraw:
                self._wantRedraw = False
                rr.redrawPlayers = True
                #print('Drawing',self.playerId,'at',self._pos,'with offsets',self._xoff,',',self._yoff)
                #rr.addFg(DrawTask(self.sprite, self._makeX(self._pos), self._makeY(self._pos)))
            if self._pendingAction != Action.NONE:
                aniDelta = Action.asDeltaPos(self._pendingAction)
                # Check if we are moving into a space - TODO: Room
                if world.isFreeSpace(self._currentRoom, self._pos.plus(aniDelta)):
                    self._applyPendingAction()
                self._pendingAction = Action.NONE

    def _applyPendingAction(self):
        action = self._pendingAction
        self._aniDelta = Action.asDeltaPos(action)

        if not self._aniDelta.isEmpty():
            print('Starting move from pos',self._pos,'using aniDelta',self._aniDelta,'from action of',action)
            # We are going to animate from the current position to the new position
            self._animating = self.NumberOfAnimationSteps
            self._aniAction = action
            self._aniPos = self._pos
            print("Changing pos from", self._pos)
            self._pos = self._pos.plus(self._aniDelta)
            print("Changed pos to",self._pos)
            self._xoff = 0
            self._yoff = 0
            # Consumed this action now
        else:
            print('No move cos',action,' so using', self._aniDelta)

    def actionFromKey(self, k):
        if k == self.keySet.right: return Action.MOVE_RIGHT
        elif k == self.keySet.left: return Action.MOVE_LEFT
        elif k == self.keySet.up: return Action.MOVE_UP
        elif k == self.keySet.down: return Action.MOVE_DOWN
        else: return Action.NONE

