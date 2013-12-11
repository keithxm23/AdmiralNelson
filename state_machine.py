class BotState(object):

    def __init__(self, name):
        self.name = name

        self.is_attacker = False
        self.is_defender = False
        self.panic_mode = False

    def __repr__(self):
        return self.name

    def get_order(self):
        """
        Actions to perform every tick that entity is in this state
        """
        pass

    def entry_actions(self):
        """
        Actions to perform at tick immediately after entering a state
        """
        pass

    def exit_actions(self):
        """
        Actions to perform at tick just before exiting a state
        """
        pass



class StateMachine(object):

    def __init__(self, commander):
        self.commander = commander

    def process(self, commander):
        pass



        for bot in commander.bot_states:
            pass
            # give bot order if idle



    def think(self):
         # Only continue if there is an active state
        if self.active_state is None:
            return

        # Perform the actions of the active state, and check conditions
        self.active_state.do_actions()
        new_state_name = self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, new_state_name):
        # Change states and perform any exit / entry actions
        if self.active_state is not None:
            self.active_state.exit_actions()
            self.active_state = self.states[new_state_name]
            self.active_state.entry_actions()
