
from NonPlainarSlicing import mesh_object

from .utils import *
from .file_read import *
from .file_write import *

from NonPlainarSlicing.globals  import Glob


class Gcode:

    gcode_out = []
    offset = []

    def __init__(self, path : str, meshobject , l: float) -> None:
       
        
        command_list = readGcodeFileToDicList(path)
        
        Glob.set_progress(0.5)
        command_list_index_of_points, command_list_points, mask_is_mesh = get_points_from_commands(command_list)

        Glob.set_progress(0.6)
        command_list_points[:,2] = np.where(np.any(np.isnan(command_list_points[:, :2]), axis=1),np.nan, command_list_points[:,2] )
        offset = get_offset_form_origan(command_list, command_list_index_of_points[mask_is_mesh], command_list_points[mask_is_mesh])
        Glob.set_progress(0.7)
        command_list_index_of_points, command_list_points = segmentise_lines(command_list_index_of_points, command_list_points, l)
        Glob.set_progress(0.8)
        shift_points(command_list_points, -offset)
        Glob.set_progress(0.85)
        command_list_points = self.z_back_trans(command_list_points, meshobject)
        
        z_min = np.nanmin(command_list_points[:, 2])
        print("z min:" + str(z_min))
        offset[2] =  -z_min +0.35

        shift_points(command_list_points, offset)
        Glob.set_progress(0.95)
        z_min = np.nanmin(command_list_points[:, 2])
        if z_min < 0:
            raise ZMinCollisionException(z_min) 

        
        self.gcode_out = to_gcode_list(command_list, command_list_index_of_points, command_list_points)
        Glob.set_progress(1)

    


    def z_back_trans(self, command_list_points, mesh:mesh_object.MeshObject):

        Glob.set_progress2(0.2)
        print("start - zBackTrans")
        mask = ~np.any(np.isnan(command_list_points), axis=1)
        Glob.set_progress2(0.3)
        locations, index_ray = mesh.distort_on_trans(command_list_points[mask, :3])
        Glob.set_progress2(0.7)
        #commandListPoints[mask][index_ray, 2] -= locations[:, 2]
        command_list_points[np.where(mask)[0][index_ray], 2] -= locations[:, 2]
        #commandListPoints[mask][index_ray, 2] = commandListPoints[mask][index_ray, 2] -  locations[:, 2]
        print("end - zBackTrans")
        Glob.set_progress2(0.9)
        return command_list_points


    
class ZMinCollisionException(Exception):
    def __init__(self, z_min):
        self.z_min = z_min
        super().__init__(self.__str__())

    def __str__(self):
        return (
            f"Z Min is under 0: {self.z_min}. Nozzle would collide with the build plate. "
            "Check if you have the correct G-code."
        )

