import time
from subprocess import call
import os
from Mock import *

mock = Mock('mockingBird')
print "FSM name: ", mock.name
time.sleep(0.5)
print mock.state
mock.launch()
print "Communicate with OS: ", os.path.exists('/reg/d/psdm')
print "Execute programs:"
call(['ps'])
time.sleep(2)
print mock.state
mock.doneProcessing()
time.sleep(1)
print mock.state
mock.endOfRun()
time.sleep(0.5)
print mock.state

