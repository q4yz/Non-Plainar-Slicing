#from .gcode_util_interface import GcodeUtilities  GcodeUtilities
import trimesh

from .helper.file_read import helper_read_gcode_file_to_dic_list
from .helper.utils import helper_get_points_from_commands
import numpy as np
from .commands import Commands
from ..mesh_utilities.helpers.projection_on_plain import distort_vertices_on_plain

class GcodeUtils:

    @staticmethod
    def read_gcode_file_to_dic_list(file_path):
        return helper_read_gcode_file_to_dic_list(file_path)

    @staticmethod
    def points_from_commands(command_list):
        return helper_get_points_from_commands(command_list)

    @staticmethod
    def offset_form_origin(commands):
        command_list = commands.command_list
        points_list = commands.get_points()
        mask = GcodeUtils.get_g1_command_points(command_list, commands.get_command_index())


        command_list_points_g1 = points_list[mask]
        boundingbox = GcodeUtils.boundingbox(command_list_points_g1)

        print("bounding" , str(boundingbox))

        min_values = boundingbox[0]
        max_values = boundingbox[1]
        center = min_values + (max_values - min_values) / 2
        offset = np.array((center[0], center[1], 0))
        return offset


    @staticmethod
    def get_g1_command_points (command_list, index_command):
        mask_g1 = np.zeros_like(index_command, dtype=bool)
        #print(command_list)
        #print(points_list)

        for i, index in enumerate(index_command):

            if command_list[index]["command"] == "G1":
                mask_g1[i] = True



        return mask_g1

    @staticmethod
    def boundingbox(list_points):

        min_xyz = np.nanmin(list_points[:,:3], axis=0)
        max_xyz = np.nanmax(list_points[:,:3], axis=0)
        return np.vstack((min_xyz, max_xyz))


    @staticmethod
    def segment_lines(old_commands: Commands,threshold):

        new_commands = Commands(old_commands.command_list)
        print("start - segment Lines")

        threshold_sqr = threshold ** 2
        current_xyze = np.array([])

        for i in range(old_commands.count):
            point = old_commands.getValue(i)
            index = point[0]
            xyzef = point[1]
            is_mesh = point[2]
            if np.any(np.isnan(xyzef[:4])):
                new_commands.append(idx=index , xyzef=xyzef, is_mesh=is_mesh)

            elif current_xyze.size == 0:
                current_xyze = xyzef[:4]
                new_commands.append(idx=index, xyzef=xyzef, is_mesh=is_mesh)

            else:
                end_point = np.where(np.isnan(xyzef[:4]), current_xyze, xyzef[:4])
                distance_sqr = np.sum((current_xyze[:-1] - end_point[:-1]) ** 2)

                num_segments = int(np.ceil(np.sqrt(distance_sqr) / threshold)) if distance_sqr > threshold_sqr else 2
                new_commands.extend(index, (np.linspace(current_xyze, end_point, num=num_segments)[1:]), xyzef[4], is_mesh  )

                current_xyze = end_point

        old_commands.override(new_commands)

    @staticmethod
    def transform_back_gcode_on_plain(commands, plain: trimesh.Trimesh):
        print("start - zBackTrans")


        points = commands.get_points()
        mask = ~np.any(np.isnan(points[:,:3]), axis=1)
        sub_points = points[mask,:3]

        plain.apply_scale([1, 1, -1])
        distort_vertices_on_plain(plain, sub_points)
        plain.apply_scale([1, 1, -1])

        points[mask,:3] = sub_points

        #commands.set_points(points)



        print("end - zBackTrans")
        #Glob.get_sub_tracker().set_progress(0.9)
        #return command_list_points
        pass

    @staticmethod
    def export(commands, path):

        out_commands = commands.get_string_list()
        print(out_commands)
        try:
            with open(path, 'w') as file:
                for command in out_commands:
                    file.write(command + '\n')
        except Exception as e:
            print(f"Error writing to file: {e}")
        else:
            print("File written successfully.")

        print("end - printTofile")












"""
z_min = np.nanmin(command_list_points[:, 2])
    if z_min < 0:
        raise ZMinCollisionException(z_min)
class ZMinCollisionException(Exception):
    def __init__(self, z_min):
        self.z_min = z_min
        super().__init__(self.__str__())

    def __str__(self):
        return (
            f"Z Min is under 0: {self.z_min}. Nozzle would collide with the build plate. "
            "Check if you have the correct G-code."
        )"""
