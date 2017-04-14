from transitions import Machine

class Batch(object):

    # Define some states.
    states = ['idle', 'processing', 'doneRun', 'exit']

    def __init__(self, name):

        # Name of this slave is defined by the #hashtag
        self.name = name

        # Initialize the state machine
        self.machine = Machine(model=self, states=Batch.states, initial='idle')

        # Launch
        self.machine.add_transition(trigger='launch', source='idle', dest='processing')

        # Indexing
        self.machine.add_transition(trigger='doneProcessing', source='processing', dest='doneRun', after='cleanUp')

        # Exit
        self.machine.add_transition(trigger='endOfRun', source='doneRun', dest='exit')

    def cleanUp(self):
        # delete temporary files
        print "Done cleaning up"





