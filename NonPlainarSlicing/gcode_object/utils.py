from pickle import NONE
from xmlrpc.client import boolean
import numpy as np
from NonPlainarSlicing.globals  import Glob

def get_offset_form_origan (command_list, command_list_index_of_points, command_list_points):


    command_list_points_g1 = get_g1_command_points(command_list, command_list_index_of_points, command_list_points)

    boundingbox =  get_boundingbox(command_list_points_g1)

    print("bounding" + str(boundingbox))
    
    min_values = boundingbox[0]
    max_values = boundingbox[1]
    center = min_values + (max_values - min_values)/2
    offset = np.array((center[0],center[1],0))
    return offset



def get_g1_command_points (command_list, command_listidex_of_points, command_list_points):
    mask_g1 = np.fromiter((list(command_list[i].values())[0] == "G1" for i in command_listidex_of_points), dtype=bool)
    command_list_points_g1 = command_list_points[mask_g1]
    return command_list_points_g1

def get_boundingbox(list_points):
    min_xyz = np.nanmin(list_points, axis=0)
    max_xyz = np.nanmax(list_points, axis=0)
    boundindbox = np.vstack((min_xyz, max_xyz))

    return boundindbox



def get_points_from_commands(command_list):
    print("start - getPointsFromCommands")
    command_list_points = np.empty((len(command_list), 4))  # Pre-allocate the array
    command_list_index_of_points = np.empty(len(command_list), dtype=int)
    mask_is_mesh = np.empty(len(command_list), dtype=bool)
    point_count = 0 
    currently_mesh = True
    last_vertice = [None,None,None,None]

    for idx, command in enumerate(command_list):
        if command['command'].startswith(";MESH:NONMESH"):
            #currentlyMesh = False
            pass
        elif command['command'].startswith(";MESH:"):
            #currentlyMesh = True
            pass

        elif command['command'] == 'G1' or command['command'] == 'G0': 
            params = command.get('parameters', {})
            x = params.get('X', last_vertice[0])
            y = params.get('Y', last_vertice[1])
            z = params.get('Z', last_vertice[2])
            e = params.get('E', last_vertice[3])
            
            command_list_points[point_count] = [x, y, z, e]
            command_list_index_of_points[point_count] = idx
            mask_is_mesh[point_count] = currently_mesh

            point_count += 1 
            last_vertice = [x,y,z,e]

    command_list_points = command_list_points[:point_count]
    command_list_index_of_points = command_list_index_of_points[:point_count]
    mask_is_mesh = mask_is_mesh[:point_count]
    print("end - get points from commands")
    return command_list_index_of_points, command_list_points, mask_is_mesh


def segmentise_lines(points_index, point_list, threshold):
        print("start - segment Lines")
        point_list = np.array(point_list, dtype=np.float32)
      
        threshold_sqr = threshold**2
        current_xyze = np.array([])
        points_out = np.empty((0, 4), dtype=np.float32)
        index_out = np.empty(0, dtype=np.int16)

        step = 0
        total_steps = len(points_index)

        for index, point in zip(points_index, point_list):
            Glob.progress2 = step / float(total_steps)
            step+= 1
            if np.any(np.isnan(point)):
                points_out = np.vstack((points_out, point))
                index_out = np.append( index_out ,np.full(1,index))
            elif current_xyze.size == 0:
                current_xyze = point
                points_out = np.vstack((points_out, point))
                index_out = np.append( index_out ,np.full(1,index))
                
            else:
                endPoint = np.where(np.isnan(point), current_xyze, point)
                distanceSqr = np.sum((current_xyze[:-1] - endPoint[:-1]) ** 2)
    
                if distanceSqr > threshold_sqr:
                    num_segments = int(np.ceil(np.sqrt(distanceSqr) / 4))
                else:
                    num_segments = 2  

                num_segments = int(np.ceil(np.sqrt(distanceSqr) / threshold)) if distanceSqr > threshold_sqr else 2
                points_out = np.vstack((points_out, np.linspace(current_xyze, endPoint, num=num_segments)[1:]))
                index_out = np.append( index_out ,np.full(num_segments -1,index))
                current_xyze = endPoint
      
        print("end - segmentizeLines")
        return index_out, points_out


def shift_points(points, offset) -> np.array:
    offset = np.append(offset, 0)
    points[:, :4] += offset

    return points

   