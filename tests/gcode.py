
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), r"..\NonePlainarSlicing")))


print(sys.path)
import gcode_object



g = gcode_object.Gcode(None, None)