import sys
import logging
import numpy as np
from PyQt5 import QtWidgets

from NonPlainarSlicing import MainWindow
from NonPlainarSlicing.gcode_utilities.gcode_object import GcodeObject
# --------------------
# Configure logging
# --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# --------------------
# Numpy display settings
# --------------------
np.set_printoptions(precision=4, suppress=True, edgeitems=8, threshold=40)

# --------------------
# App entry point
# --------------------
def main():




    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()



"""
path = r'C:\Daten\Test-Slicer\Gcode_IN\CFFFP_out - Kopie.gcode'

    g = GcodeObject(path)
    print(g.commands.get_points())
    print(g.get_offset_form_origin())
    print(g.move_to_center())
    print(g.get_offset_form_origin())
    print(g.commands.count)
    g.segment_lines(1)
    print(g.commands.count)


    exit()"""