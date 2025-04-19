from abc import ABC, abstractmethod
import trimesh
import numpy as np

from ..globals import ProgressTracker
from ..globals import Settings



class GcodeUtilities(ABC):

    @staticmethod
    @abstractmethod
    def read_gcode_file_to_dic_list(file_path):
        pass

    @staticmethod
    @abstractmethod
    def get_points_from_commands(command_list):
        pass

"""
    export
    to_gcode_list

    z_back_trans
    ZMinCollisionException

    get_offset_form_origan
    get_g1_command_points
    get_boundingbox
    get_offset_form_origan
    get_points_from_commands
    segmentise_lines

    shift_points
    

"""
