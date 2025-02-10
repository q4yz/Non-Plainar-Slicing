import numpy as np

import mesh_object


from .utils import *
from .file_read import *
from .file_write import *

import globals


class Gcode():

    gcode_out = []
    offset = []

    def __init__(self, path : str, meshobject , l: float) -> None:
       
        
        commandList = readGcodeFileToDicList(path)
        
        globals.progress = 0.5
        commandListidexOfPoints, commandListPoints, maskIsMesh = getPointsFromCommands(commandList)
        globals.progress = 0.6
        commandListPoints[:,2] = np.where(np.any(np.isnan(commandListPoints[:, :2]), axis=1),np.nan, commandListPoints[:,2] )
        offset = getOffsetFormOrigan(commandList, commandListidexOfPoints[maskIsMesh], commandListPoints[maskIsMesh])
        globals.progress = 0.7
        commandListidexOfPoints, commandListPoints = segmentizeLines(commandListidexOfPoints, commandListPoints,l)    
        globals.progress = 0.8
        shiftPoints(commandListPoints, -offset )
        globals.progress = 0.85
        commandListPoints = self.zBackTrans(commandListPoints, meshobject)
        
        z_min = np.nanmin(commandListPoints[:, 2])
        print("z min:" + str(z_min))
        offset[2] =  -z_min +0.35

        shiftPoints(commandListPoints, offset )
        globals.progress = 0.95
        z_min = np.nanmin(commandListPoints[:, 2])
        if z_min < 0:
            raise ZMinCollisionException(z_min) 

        
        self.gcode_out = toGcodeList(commandList, commandListidexOfPoints, commandListPoints )
        globals.progress = 1

    


    def zBackTrans(self, commandListPoints, mesh:mesh_object.MeshObject):
        globals.progress2 = 0.2
            
        print("start - zBackTrans")
        mask = ~np.any(np.isnan(commandListPoints),axis=1)
        globals.progress2 = 0.3
        locations, index_ray = mesh.distortOnTrans(commandListPoints[mask,:3])
        globals.progress2 = 0.7
        #commandListPoints[mask][index_ray, 2] -= locations[:, 2]
        commandListPoints[np.where(mask)[0][index_ray], 2] -= locations[:, 2]
        #commandListPoints[mask][index_ray, 2] = commandListPoints[mask][index_ray, 2] -  locations[:, 2]
        print("end - zBackTrans")
        globals.progress2 = 0.9
        return commandListPoints


    
class ZMinCollisionException(Exception):
    def __init__(self, z_min):
        self.z_min = z_min
        super().__init__(self.__str__())

    def __str__(self):
        return (
            f"Z Min is under 0: {self.z_min}. Zozze would collide with the build plate. "
            "Check if you have the correct G-code."
        )

