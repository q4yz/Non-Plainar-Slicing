
import logging
from Viewer import Viewer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

# Start the Viewer
np.set_printoptions(precision=4, suppress=True, edgeitems=8)  

if __name__ == "__main__":
    Viewer()