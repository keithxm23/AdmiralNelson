from state_machine import BotState
from api.vector2 import Vector2
from api import orders
import random
from a_star import AStar

class BotStateIdle(BotState):

    def __init__(self):
        BotState.__init__(self, "IDLE")


    def get_order(self, commander):
        pass


class BotStateDefend(BotState):

    def __init__(self):
        BotState.__init__(self, "DEFEND")



    def get_order(self, commander, bot):


        exact_target = commander.level.findRandomFreePositionInBox((commander.game.team.flag.position - 5.0, commander.game.team.flag.position + 5.0))
        pomastar = AStar(commander.gamedata['blockHeights'], commander.twodpom)
        path = pomastar.get_path(bot.position.x,
                              bot.position.y,
                              exact_target.x,
                              exact_target.y)

        try:
            if len(path) > 10:
                exact_target = Vector2(*path[len(path)/2])
                target = commander.level.findRandomFreePositionInBox((exact_target-5.0, exact_target+5.0))
            else:
                target = commander.game.team.flag.position
            # print target
            if not target:
                raise "no target found"

        except:
            print 'couldnt convert target to vec2'
            target = flagScoreLocation = commander.game.team.flagScoreLocation



        targetMin = target - Vector2(2.0, 2.0)
        targetMax = target + Vector2(2.0, 2.0)
        goal = commander.level.findRandomFreePositionInBox([targetMin, targetMax])

        if not goal:
            return None, None

        if (goal - bot.position).length() > 8.0:
            return (orders.Charge, commander.defender, goal), {'description' : 'rushing to defend'}
        else:
            return (orders.Defend, commander.defender, (commander.middle - bot.position)), {'description' : 'defending'}



class BotStateAttackFlag(BotState):

    def __init__(self):
        BotState.__init__(self, "Attack Flag")



    def get_order(self, commander, bot):
        if bot.flag:
            # Tell the flag carrier to run home!
            target = commander.game.team.flagScoreLocation
            return (orders.Charge, bot, target), {'description' : 'run home'}

        else:
            target = commander.game.enemyTeam.flag.position
            flank = commander.getFlankingPosition(bot, target)
            if (target - flank).length() > (bot.position - target).length():
                return (orders.Attack, bot, target), {'description' : 'attack from flank', 'lookAt':target}
            else:
                flank = commander.level.findNearestFreePosition(flank)
                return (orders.Charge, bot, flank), { 'description' : 'running to flank'}

class BotStateRandomPatrol(BotState):

    def __init__(self):
        BotState.__init__(self, "Random Patrol")



    def get_order(self, commander, bot):
        try:
            halfBox = 0.4 * min(commander.level.width, commander.level.height) * Vector2(1, 1)

            exact_target = commander.level.findRandomFreePositionInBox((commander.middle - halfBox, commander.middle + halfBox))
            path = commander.astar.get_path(bot.position.x,
                                  bot.position.y,
                                  exact_target.x,
                                  exact_target.y)

            try:
                if len(path) > 10:
                    exact_target = Vector2(*path[len(path)/2])
                    target = commander.level.findRandomFreePositionInBox((exact_target-5.0, exact_target+5.0))
                else:
                    target = commander.game.team.flagScoreLocation
                # print target
                if not target:
                    raise "no target found"

            except:
                print 'couldnt convert target to vec2'
                target = flagScoreLocation = commander.game.team.flagScoreLocation
        except:
            halfBox = 0.4 * min(commander.level.width, commander.level.height) * Vector2(1, 1)

            target = commander.level.findRandomFreePositionInBox((commander.middle - halfBox, commander.middle + halfBox))

            # issue the order
            if target:
                return (orders.Attack, bot, target), {'description': 'random patrol'}


        # issue the order
        if target:
            return (orders.Attack, bot, target), {'description': 'random patrol'}
        else:
            return None, None

class BotStateAttackBot(BotState):

    def __init__(self):
        BotState.__init__(self, "Attack Bot")



    def get_order(self, commander, bot):
        target = commander.level.findRandomFreePositionInBox((bot.position-5.0, bot.position+5.0))
        if target:
            return (orders.Attack, bot, target), {'lookAt' : random.choice([b.position for b in bot.visibleEnemies])}
        else:
            return None, None


class BotStateInterceptFlag(BotState):

    def __init__(self):
        BotState.__init__(self, "Intercept Flag")

    def get_order(self, commander, bot):
        targetPosition = (commander.game.team.flag.position + commander.game.enemyTeam.flagScoreLocation) * 0.5
        targetMin = targetPosition - Vector2(6.0, 6.0)
        targetMax = targetPosition + Vector2(6.0, 6.0)
        goal = commander.level.findRandomFreePositionInBox([targetMin, targetMax])

        if goal:
            return (orders.Attack, bot, goal), {'description' : 'running to intercept', 'lookAt' : targetPosition}
        else:
            return None, None