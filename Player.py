
from PmzGraphics import *
from GameController import *


class KeySet:
    def __init__(self, left, right, up, down):
        self.left = left
        self.right = right
        self.up = up
        self.down = down


class Constants:
    keySets = [
        # Left, right, up, down
        KeySet(pygame.K_z, pygame.K_x, pygame.K_f, pygame.K_c),
        KeySet(pygame.K_1, pygame.K_q, pygame.K_e, pygame.K_w),
        KeySet(pygame.K_b, pygame.K_n, pygame.K_i, pygame.K_j),
        KeySet(pygame.K_l, pygame.K_p, pygame.K_9, pygame.K_o)
    ]


class Player():
    def __init__(self, playerId, isLocal, sprite, xpos, ypos):
        self.keySet = Constants.keySets[playerId]
        self.playerId = playerId
        self.isLocal = isLocal
        self._animating = 0
        self.sprite = sprite
        self._pos = Pos(xpos, ypos)
        self.xoff = 0
        self.yoff = 0
        self.w = sprite.w
        self.h = sprite.h
        self._pendingAction = Action.NONE
        self._wantRedraw = True
        print('Got h of',self.h)

    def __str__(self):
        return "Player("+str(self.playerId)+", local="+str(self.isLocal)+", sprite='"+self.sprite.name+"', pos="+str(self._pos)+")"

    def isBusy(self):
        return self._animating != 0

    def takeAction(self, action):
        print('takeAction called with',action)
        self._pendingAction = action

    def update(self, world, rr):
        if self._animating > 0:
            self._animating -= 1
            self._animate(rr)
        else:
            if self._wantRedraw:
                self.xoff = 0
                self.yoff = 0
                rr.addFg(DrawTask(self.sprite, self._makeX(self._pos), self._makeY(self._pos)))
                self._wantRedraw = False
            if self._pendingAction != Action.NONE:
                aniDelta = Action.asDeltaPos(self._pendingAction)
                # Check if we are moving into a space - TODO: Room
                if world.isFreeSpace(world._currentRoom, self._pos.plus(aniDelta)):
                    self._applyPendingAction()
                self._pendingAction = Action.NONE

    def _applyPendingAction(self):
        action = self._pendingAction
        self._aniDelta = Action.asDeltaPos(action)

        if not self._aniDelta.isEmpty():
            print('Starting move using ', self._aniDelta,'from action of',action)
            # We are going to animate from the current position to the new position
            self._animating = 20
            self._aniAction = action
            self._aniPos = self._pos
            self._pos = self._pos.plus(self._aniDelta)
            self.xoff = 0
            self.yoff = 0
            # Consumed this action now
        else:
            print('No move cos',action,' so using', self._aniDelta)

    def _animate(self, rr):
        if self._aniAction == Action.MOVE_RIGHT:
            rr.addBg(UndrawTask(self._makeX(self._aniPos), self._makeY(self._aniPos), 50, self.h))
            self.xoff += 5
        elif self._aniAction == Action.MOVE_LEFT:
            rr.addBg(UndrawTask(self._makeX(self._aniPos)+self.w-50, self._makeY(self._aniPos), 50, self.h))
            self.xoff -= 5
        elif self._aniAction == Action.MOVE_UP:
            rr.addBg(UndrawTask(self._makeX(self._aniPos), self._makeY(self._aniPos)+self.h*0.4, self.w, self.h*0.6))
            self.yoff -= 4
        elif self._aniAction == Action.MOVE_DOWN:
            rr.addBg(UndrawTask(self._makeX(self._aniPos), self._makeY(self._aniPos), self.w, self.h*0.66))
            self.yoff += 4
        rr.addFg(DrawTask(self.sprite, self._makeX(self._aniPos), self._makeY(self._aniPos)))

    def _makeX(self, pos): return pos.x() * 100  + self.xoff
                 
    def _makeY(self, pos): return pos.y() * 80   + self.yoff-40
        
    def actionFromKey(self, k):
        if k == self.keySet.right: return Action.MOVE_RIGHT
        elif k == self.keySet.left: return Action.MOVE_LEFT
        elif k == self.keySet.up: return Action.MOVE_UP
        elif k == self.keySet.down: return Action.MOVE_DOWN
        else: return Action.NONE

