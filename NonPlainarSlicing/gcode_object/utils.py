from pickle import NONE
from xmlrpc.client import boolean
import numpy as np




def getOffsetFormOrigan (commandList, commandListidexOfPoints, commandListPoints):


    commandListPointsG1 = getG1CommandPoints(commandList, commandListidexOfPoints, commandListPoints)
    print(commandListPointsG1)
    mask = (commandListPointsG1[:, 0] != 0) & (commandListPointsG1[:, 1] != 0)

    boundingbox =  getBoundingbox(commandListPointsG1[mask])

    print("bounding" + str(boundingbox))
    
    min_values = boundingbox[0]
    max_values = boundingbox[1]
    center = min_values + (max_values - min_values)/2
    offset = np.array((center[0],center[1],0))  #min_values[2]
    return offset



def getG1CommandPoints (commandList, commandListidexOfPoints, commandListPoints):
    maskG1 = np.fromiter((list(commandList[i].values())[0] == "G1" for i in commandListidexOfPoints) , dtype=bool)
    commandListPointsG1 = commandListPoints[maskG1]
    return commandListPointsG1

def getAvgCenter(listPoints):
    avg_center = np.avg(listPoints, axis=0)
    return avg_center

def getBoundingbox(listPoints):
    print(listPoints)
    min_xyz = np.min(listPoints, axis=0)
    max_xyz = np.max(listPoints, axis=0)
    boundindbox = np.vstack((min_xyz, max_xyz))

    return boundindbox



def getPointsFromCommands( commandList):
    print("start - getPointsFromCommands")
    commandListPoints = np.empty((len(commandList), 4))  # Pre-allocate the array
    commandListidexOfPoints = np.empty(len(commandList), dtype=int)
    maskIsMesh = np.empty(len(commandList), dtype=bool)
    point_count = 0 
    currentlyMesh = False
    lastVertice = [None,None,None,None]

    for idx, command in enumerate(commandList):
        if command['command'].startswith(";MESH:NONMESH"):
            currentlyMesh = False
        elif command['command'].startswith(";MESH:"):
            currentlyMesh = True

        elif command['command'] == 'G1' or command['command'] == 'G0': 
            params = command.get('parameters', {})
            x = params.get('X', lastVertice[0])
            y = params.get('Y', lastVertice[1])
            z = params.get('Z', lastVertice[2])  
            e = params.get('E', lastVertice[3])  
            
            commandListPoints[point_count] = [x, y, z, e]
            commandListidexOfPoints[point_count] = idx
            maskIsMesh[point_count] = currentlyMesh

            point_count += 1 
            lastVertice = [x,y,z,e]

    commandListPoints = commandListPoints[:point_count]
    commandListidexOfPoints = commandListidexOfPoints[:point_count]
    maskIsMesh = maskIsMesh[:point_count]
    print("end - getPointsFromCommands")
    return commandListidexOfPoints, commandListPoints, maskIsMesh


#def segmentizeLines(pointsIndex, pointList, threshold):
#    print("start - segmentizeLines")
    
#    pointList = np.array(pointList, dtype=np.float32)  # Use float32 for better performance
#    thresholdSqr = threshold ** 2
#    currentXYZE = np.zeros(4, dtype=np.float32)

#    estimated_size = len(pointList) * 3  # Overestimate initial size
#    points_out = np.empty((estimated_size, 4), dtype=np.float32)
#    index_out = np.empty(estimated_size, dtype=np.int32)

#    count = 0  # Tracks the number of used elements

#    for index, point in zip(pointsIndex, pointList):
#        if count >= len(points_out):  # Resize if needed
#            new_size = len(points_out) * 2  # Double the size
#            points_out = np.resize(points_out, (new_size, 4))
#            index_out = np.resize(index_out, new_size)

#        if np.any(np.isnan(point)):  # Handle NaN points
#            points_out[count] = point
#            index_out[count] = index
#            count += 1
#        else:
#            endPoint = np.where(np.isnan(point), currentXYZE, point)
#            distanceSqr = np.sum((currentXYZE[:-1] - endPoint[:-1]) ** 2)

#            num_segments = int(np.ceil(np.sqrt(distanceSqr) / threshold)) if distanceSqr > thresholdSqr else 2
#            segment_points = np.linspace(currentXYZE, endPoint, num=num_segments)[1:]  # Exclude first point

#            num_new_points = len(segment_points)

#            # Resize again if needed
#            while count + num_new_points >= len(points_out):
#                new_size = len(points_out) * 2  # Double the size
#                points_out = np.resize(points_out, (new_size, 4))
#                index_out = np.resize(index_out, new_size)

#            # Store new points
#            points_out[count:count + num_new_points] = segment_points
#            index_out[count:count + num_new_points] = index
#            count += num_new_points

#            currentXYZE = endPoint

#    print("end - segmentizeLines")
    
#    return index_out[:count], points_out[:count]  # Trim to actual size

def segmentizeLines(pointsIndex,pointList, threshold  ):
        print("start - segmentizeLines")
        pointList = np.array(pointList, dtype=np.float32)
        print(pointList)
        thresholdSqr = threshold**2
        currentXYZE = np.array([])
        points_out = np.empty((0, 4), dtype=np.float32)
        index_out = np.empty(0, dtype=np.int16)

        for index, point in zip(pointsIndex,pointList):

            if np.any(np.isnan(point)):
                points_out = np.vstack((points_out, (point)))
                index_out = np.append( index_out ,np.full(1,index))
            elif currentXYZE.size == 0:
                currentXYZE = point
                points_out = np.vstack((points_out, (point)))
                index_out = np.append( index_out ,np.full(1,index))
                
            else:
                endPoint = np.where(np.isnan(point), currentXYZE, point)
                distanceSqr = np.sum((currentXYZE[:-1] - endPoint[:-1]) ** 2)
    
                if distanceSqr > thresholdSqr:
                    num_segments = int(np.ceil(np.sqrt(distanceSqr) / 4))
                else:
                    num_segments = 2  

                num_segments = int(np.ceil(np.sqrt(distanceSqr) / threshold)) if distanceSqr > thresholdSqr else 2
                points_out = np.vstack((points_out, np.linspace(currentXYZE, endPoint, num=num_segments)[1:]))
                index_out = np.append( index_out ,np.full(num_segments -1,index))
                currentXYZE = endPoint
        print(points_out)
        print("end - segmentizeLines")
        return index_out, points_out


def shiftPoints( points, offset):
    offset = np.append(offset, 0)
    points[:, :4] += offset

    return points

   