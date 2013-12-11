# Your AI for CTF must inherit from the base Commander class.  See how this is
# implemented by looking at the commander.py in the ./api/ folder.
from api.commander import Commander

# The commander can send orders to individual bots.  These are listed and
# documented in orders.py from the ./api/ folder also.
from api import orders

# The maps for CTF are layed out along the X and Z axis in space, but can be
# effectively be considered 2D.
from api.vector2 import Vector2

import cPickle as pickle
from visibility import get_visibility_map
from a_star import AStar
import time

from game_constants import gameplayDataFilepath
from pom import ProbOccurenceMaps
from visible_view import VisibleView

from state_machine import *
from bot_states import *
import numpy as np

class AdmNelson(Commander):
    """
    Rename and modify this class to create your own commander and add mycmd.Placeholder
    to the execution command you use to run the competition.
    """

    def initialize(self):
        """Use this function to setup your bot before the game starts."""
        self.verbose = True    # display the order descriptions next to the bot labels
        self.gamedata = {}  # stores game state to be pickled later and used by visualize.py
        self.gamedata['blockHeights'] = self.level.blockHeights
        self.gamedata['visibility_map'] = get_visibility_map(self.level.blockHeights)
        self.astar = AStar(self.gamedata['blockHeights'], self.gamedata['visibility_map'].tolist())

        self.visibleView = VisibleView(self.level.fieldOfViewAngles, self.level.blockHeights, self.game.team, self.game.enemyTeam)
        #self.pom = ProbOccurenceMap(self.level.blockHeights)
        self.poms = ProbOccurenceMaps(self.level.blockHeights, self.game.enemyTeam)
        
        self.blockHeights = self.level.blockHeights
        #self.gamedata['probOccMap'] = self.pom.prob

        self.attacker = None
        self.defender = None
        self.verbose = True

        # Calculate flag positions and store the middle.
        ours = self.game.team.flag.position
        theirs = self.game.enemyTeam.flag.position
        self.middle = (theirs + ours) * 0.5

        # Now figure out the flaking directions, assumed perpendicular.
        d = (ours - theirs)
        self.left = Vector2(-d.y, d.x).normalized()
        self.right = Vector2(d.y, -d.x).normalized()
        self.front = Vector2(d.x, d.y).normalized()

        self.panicMode = False

        self.bot_states = dict([(bot.name, BotStateIdle()) for bot in self.game.team.members])

        self.attacker = None
        self.defender = None


    def tick(self):
        """Override this function for your own bots.  Here you can access all the information in self.game,
        which includes game information, and self.level which includes information about the level."""

        visibleNodes, visibleEnemyNodes = self.visibleView.tick()
        #self.pom.tick(visibleNodes, visibleEnemyNodes)
        self.poms.tick(visibleNodes, visibleEnemyNodes)

        #Save the game state to a pickle so that it can be used by visualize.py
        output = open(gameplayDataFilepath, "wb")
        self.gamedata['bot_positions'] = []
        self.gamedata['probOccMap'] = self.poms.getCombinedPom()
        self.gamedata['visibleNodes'] = visibleNodes
        pom = self.gamedata['probOccMap']
        for b in self.game.bots_alive:
            self.gamedata['bot_positions'].append((int(round(b.position.x)), int(round(b.position.y))))
        pickle.dump(self.gamedata, output)


        """
        Start commander
        """
        # print len(pom)
        self.twodpom = np.array(pom).reshape(self.level.width,self.level.height).tolist()



        for bot in self.game.bots_available:
            self.bot_states[bot.name] = BotStateIdle()


        if self.attacker and self.attacker.health <= 0:
            # the attacker is dead we'll pick another when available
            self.attacker = None

        if self.defender and (self.defender.health <= 0 or self.defender.flag):
            # the defender is dead we'll pick another when available
            #pass
            self.defender = None

        if not self.game.team.flag.carrier: # If flag is being carried by team
            self.panicMode = False # Don't panic
        else:
            if not self.panicMode: # Else if not already in panic-mode,
                self.panicMode = True # Start panicking!

                targetPosition = (self.game.team.flag.position + self.game.enemyTeam.flagScoreLocation) * 0.5
                targetMin = targetPosition - Vector2(6.0, 6.0)
                targetMax = targetPosition + Vector2(6.0, 6.0)
                goal = self.level.findRandomFreePositionInBox([targetMin, targetMax])

                if goal:
                    #Send all bots that are alive to intercept the flag
                    for bot in self.game.bots_alive:
                        if bot == self.defender or bot == self.attacker:
                            continue

                        self.bot_states[bot.name] = BotStateInterceptFlag()
                        order_args, order_keyargs = self.bot_states[bot.name].get_order(self, bot)
                        if not order_args:
                            continue
                        else:
                            self.issue(*order_args, **order_keyargs)

        # In this example we loop through all living bots without orders (self.game.bots_available)
        # All other bots will wander randomly


        for bot in self.game.bots_available:

            # If no defender, set a defender
            if (self.defender == None or self.defender == bot) and not bot.flag:
                self.defender = bot

                self.bot_states[bot.name] = BotStateDefend()
                order_args, order_keyargs = self.bot_states[bot.name].get_order(self, bot)
                if not order_args:
                    continue
                else:
                    self.issue(*order_args, **order_keyargs)



            # If no attacker, set an attacker
            elif self.attacker == None or self.attacker == bot or bot.flag:
                self.attacker = bot

                self.bot_states[bot.name] = BotStateAttackFlag()
                order_args, order_keyargs = self.bot_states[bot.name].get_order(self, bot)
                if not order_args:
                    continue
                else:
                    self.issue(*order_args, **order_keyargs)
            else:
                # All our other (random) bots

                # pick a random position in the level to move to
                self.bot_states[bot.name] = BotStateRandomPatrol()
                order_args, order_keyargs = self.bot_states[bot.name].get_order(self, bot)
                if not order_args:
                    continue
                else:
                    self.issue(*order_args, **order_keyargs)

        for bot in self.game.bots_holding:
            self.bot_states[bot.name] = BotStateAttackBot()
            order_args, order_keyargs = self.bot_states[bot.name].get_order(self, bot)
            if not order_args:
                continue
            else:
                self.issue(*order_args, **order_keyargs)




    def getFlankingPosition(self, bot, target):
        """Return simple flanking positions calculated based on the flanking vectors.

        Args:
            bot (object): The bot for which to calculate the flanking position.
            target (vector2): The location that should be flanked.

        Returns:
            The calculated flanking position as a vector2 object.
        """
        flanks = [target + f * 16.0 for f in [self.left, self.right]]
        options = map(lambda f: self.level.findNearestFreePosition(f), flanks)
        return sorted(options, key = lambda p: (bot.position - p).length())[0]

