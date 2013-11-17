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
#from visibility import get_visibility_map

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

        #TODO once you figure out how to import numpy and scipy here, directly call functions instead of using pickles as intermediary
        #self.gamedata['visibility_map'] = get_visibility_map(self.level.blockHeights)

    def tick(self):
        """Override this function for your own bots.  Here you can access all the information in self.game,
        which includes game information, and self.level which includes information about the level."""

        #Save the game state to a pickle so that it can be used by visualize.py
        output = open("C:/gamedata.p", "wb")
        self.gamedata['bot_positions'] = []
        for b in self.game.bots_alive:
            self.gamedata['bot_positions'].append((int(round(b.position.x)), int(round(b.position.y))))
        pickle.dump(self.gamedata, output)

        # for all bots which aren't currently doing anything
        for bot in self.game.bots_available:
            if bot.flag:
                # if a bot has the flag run to the scoring location
                flagScoreLocation = self.game.team.flagScoreLocation
                self.issue(orders.Charge, bot, flagScoreLocation, description = 'Run to score location')
            else:
                # otherwise run to where the flag is
                enemyFlag = self.game.enemyTeam.flag.position
                self.issue(orders.Charge, bot, enemyFlag, description = 'Run to enemy flag')

    def shutdown(self):
        """Use this function to teardown your bot after the game is over, or perform an
        analysis of the data accumulated during the game."""

        pass

