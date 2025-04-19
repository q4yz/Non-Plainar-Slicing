

from .gcode_utils import GcodeUtils
from .commands import Commands
import numpy as np

class GcodeObject:
    commands = None
    offset = [0,0,0]

    def __init__ (self, file_path):

        command_list =  GcodeUtils.read_gcode_file_to_dic_list(file_path)
        self.commands = GcodeUtils.points_from_commands(command_list)


    def move_to_center(self):
        self.offset = self.get_offset_form_origin()
        print(self.offset)
        print("offset")
        self.commands.offset_points(-self.offset)
        pass

    def move_to_original_position(self):
        self.commands.offset_points(self.offset)

    def get_offset_form_origin(self):
        return GcodeUtils.offset_form_origin(self.commands)



    def segment_lines(self, threshold):
        GcodeUtils.segment_lines(self.commands,threshold)



        pass

    def transform_back_gcode_on_plain(self, plain):
        GcodeUtils.transform_back_gcode_on_plain(self.commands,  plain)
        pass

    def export(self, path):
        GcodeUtils.export(self.commands, path)




"""

    def command_list_index_of_points, command_list_points = segment_lines(command_list_index_of_points, command_list_points, l)

    def command_list_points = self.z_back_trans(command_list_points, meshobject)

        z_min = np.nanmin(command_list_points[:, 2])
        print("z min:" + str(z_min))
        offset[2] =  -z_min +0.35






    def export(self, path):
    
    z_min = np.nanmin(command_list_points[:, 2])
        print("z min:" + str(z_min))
        offset[2] =  -z_min +0.35





    def z_back_trans(self, command_list_points, mesh):
        Glob.get_sub_tracker().set_progress(0.2)
        print("start - zBackTrans")
        mask = ~np.any(np.isnan(command_list_points), axis=1)
        Glob.get_sub_tracker().set_progress(0.3)
        locations, index_ray = mesh.distort_on_trans(command_list_points[mask, :3])
        Glob.get_sub_tracker().set_progress(0.7)

        command_list_points[np.where(mask)[0][index_ray], 2] -= locations[:, 2]

        print("end - zBackTrans")
        Glob.get_sub_tracker().set_progress(0.9)
        return command_list_points



    


"""