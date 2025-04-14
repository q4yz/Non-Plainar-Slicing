import sys
import logging
import numpy as np
from PyQt5 import QtWidgets

from NonPlainarSlicing import MainWindow

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