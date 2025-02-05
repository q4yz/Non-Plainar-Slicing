
import numpy as np

def checkForVerticesOnPlain(v) -> bool:
        maskOnPlain = v[:, 2] == 0
        return np.any(maskOnPlain)
