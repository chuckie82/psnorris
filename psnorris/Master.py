from transitions import Machine

class Master(object):

    # Define some states.
    states = ['idle', 'merge', 'phase', 'exit']

    def __init__(self, name):

        # Name of this master
        self.name = name

        # Run group that keeps track of all the runs with the same experimental condition
        self.runGroup = []

        # Number of runs merged
        self.runs_merged = 0

        # Initialize the state machine
        self.machine = Machine(model=self, states=Master.states, initial='idle')

        # Add some transitions. We could also define these using a static list of
        # dictionaries, as we did with states above, and then pass the list to
        # the Machine initializer as the transitions= argument.

        # At some point, some run will be indexed.
        self.machine.add_transition(trigger='new_indexing_results', source='idle', dest='merge', after='update_runs_merged')

        # At some point, enough runs will be merged for phasing.
        self.machine.add_transition(trigger='enough_merge', source='merge', dest='phase')

        # Not enough runs merged for phasing.
        self.machine.add_transition(trigger='not_enough_merge', source='merge', dest='idle')

        # After phasing, check if there is more data left.
        self.machine.add_transition(trigger='more_data_left', source='phase', dest='idle')

        # After phasing, exit if there are no more data left.
        self.machine.add_transition(trigger='no_data_left', source='phase', dest='exit')

    def update_runs_merged(self):
        self.runs_merged += 1

    def launch_peak_finder(self):
        # automagically find peak finding parameters
        # launch batch job with the parameters

    def kill_all_indexing_jobs(self):
        # kills all indexing jobs when a unit cell is found


