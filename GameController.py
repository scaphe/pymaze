
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
    
