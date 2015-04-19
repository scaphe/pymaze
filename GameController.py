
from PmzGraphics import Pos


# Action states
class Action:
    INIT = -1
    NONE = 0
    MOVE_RIGHT = 1
    MOVE_LEFT = 2
    MOVE_UP = 3
    MOVE_DOWN = 4

    def __init__(self, playerId, actionType):
        self.playerId = playerId
        self.actionType = actionType

    def __str__(self): return "Action(playerId="+str(self.playerId)+", actionType="+str(self.actionType)+")"

    def asDeltaPos(actionType):    
        if actionType == Action.MOVE_RIGHT: return Pos(1, 0)
        elif actionType == Action.MOVE_LEFT: return Pos(-1, 0)
        elif actionType == Action.MOVE_UP: return Pos(0, -1)
        elif actionType == Action.MOVE_DOWN: return Pos(0, 1)
        else: return Pos(0, 0)

    def isMove(actionType):
        if (actionType == Action.MOVE_RIGHT or actionType == Action.MOVE_LEFT or 
            actionType == Action.MOVE_UP or actionType == Action.MOVE_DOWN):
            return True
        else:
            return False


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

    def onPlayerMoveRequested(self, world, player, reqAction):
        return reqAction

    # e.g. handle commands like get, combine
    def onPlayerCommand(self, world, player, command): pass

    # List[worldChanges]
    def onGameTimePasses(self, world, gameTime): pass

    def onPlayerTalks(self, world, player, message): pass

    def onPlayerJoin(self, world, player): pass
    

# Immediately do stuff
class LocalGameController(GameController):
    def __init__(self, gameQueue, wrapped):
        self.gameQueue = gameQueue
        self.wrapped = wrapped

    def onPlayerMoveRequested(self, world, player, reqAction):
        action = self.wrapped.onPlayerMoveRequested(world, player, reqAction)
        self.gameQueue.put(Action(player.playerId, action))
