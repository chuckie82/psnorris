from transitions import Machine

class Slave(object):

    # Define some states.
    states = ['idle', 'peakFinding', 'indexing', 'determineUnitcell', 'doneEvent', 'exit']

    def __init__(self, name):

        # Name of this slave is defined by the #hashtag
        self.name = name

        self.numEventsDone = 0

        # Peak finding parameters
        self.peakParams = []

        # Indexing parameters
        self.indexingParams = []

        # Initialize the state machine
        self.machine = Machine(model=self, states=Slave.states, initial='idle')

        # Get an event for peak finding if available
        self.machine.add_transition(trigger='new_event', source='idle', dest='peakFinding')

        # Indexing
        self.machine.add_transition(trigger='donePeakFinding', source='peakFinding', dest='indexing', conditions=['is_hit'])
        self.machine.add_transition(trigger='donePeakFinding', source='peakFinding', dest='doneEvent', unless=['is_hit'])

        # Determine unitcell if unavailable
        self.machine.add_transition(trigger='done_indexing', source='indexing', dest='doneEvent', conditions=['has_unitcell'])
        self.machine.add_transition(trigger='done_indexing', source='indexing', dest='determineUnitcell', unless=['has_unitcell'])

        self.machine.add_transition(trigger='done_unitcell', source='determineUnitcell', dest='doneEvent')

        self.machine.add_transition(trigger='updateMachine', source='doneEvent', dest='idle', after='updateEventsDone')

        # Exit if no more events
        self.machine.add_transition(trigger='endOfRun', source='idle', dest='exit')

    def updateEventsDone(self):
        self.numEventsDone += 1

    def is_hit(self):
        # determine whether the event is a hit
        return True

    def has_unitcell(self):
        # determine whether unitcell is available
        return True



