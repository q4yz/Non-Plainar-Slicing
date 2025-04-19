from pickle import NONE
from xmlrpc.client import boolean
import numpy as np
from NonPlainarSlicing.globals import Glob
from ..commands import Commands

def get_offset_form_origan(command_list, command_list_index_of_points, command_list_points):
    command_list_points_g1 = get_g1_command_points(command_list, command_list_index_of_points, command_list_points)

    boundingbox = get_boundingbox(command_list_points_g1)

    print("bounding" + str(boundingbox))

    min_values = boundingbox[0]
    max_values = boundingbox[1]
    center = min_values + (max_values - min_values) / 2
    offset = np.array((center[0], center[1], 0))
    return offset


def get_g1_command_points(command_list, command_listidex_of_points, command_list_points):
    mask_g1 = np.fromiter((list(command_list[i].values())[0] == "G1" for i in command_listidex_of_points), dtype=bool)
    command_list_points_g1 = command_list_points[mask_g1]
    return command_list_points_g1


def get_boundingbox(list_points):
    min_xyz = np.nanmin(list_points, axis=0)
    max_xyz = np.nanmax(list_points, axis=0)
    boundindbox = np.vstack((min_xyz, max_xyz))

    return boundindbox


def helper_get_points_from_commands(command_list):
    print("start - getPointsFromCommands")
    #list_points = np.empty((len(command_list), 7),dtype=object)  # Pre-allocate the array
    currently_mesh = True
    last_vertice = [None, None, None, None]


    commands = Commands(command_list)

    for idx, command in enumerate(command_list):
        if command['command'].startswith(";MESH:NONMESH"):
            # currentlyMesh = False
            pass
        elif command['command'].startswith(";MESH:"):
            # currentlyMesh = True
            pass

        elif command['command'] == 'G1' or command['command'] == 'G0':
            params = command.get('parameters', {})
            x = params.get('X', last_vertice[0])
            y = params.get('Y', last_vertice[1])
            z = params.get('Z', last_vertice[2])
            e = params.get('E', last_vertice[3])
            f = params.get('F', np.nan)

            commands.append(idx = idx, is_mesh=currently_mesh, x=x, y=y, z=z, e=e, f=f )
            last_vertice = [x, y, z, e]


    print("end - get points from commands")

    return  commands

def shift_points(points, offset) -> np.array:
    offset = np.append(offset, 0)
    points[:, :4] += offset

    return points





