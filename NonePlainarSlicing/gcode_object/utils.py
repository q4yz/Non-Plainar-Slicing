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
    lastVertice = [0,0,0,0]

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


def segmentizeLines(pointsIndex,pointList, threshold  ):
        print("start - segmentizeLines")
        pointList = np.array(pointList, dtype=np.float16)
        thresholdSqr = threshold**2
        currentXYZE = [0,0,0,0]
        points_out = np.empty((0, 4), dtype=np.float16)
        index_out = np.empty(0, dtype=np.int16)

        for index, point in zip(pointsIndex,pointList):
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
        print("end - segmentizeLines")
        return index_out, points_out


def shiftPoints( points, offset):
    offset = np.append(offset, 0)
    points[:, :4] += offset

    return points

   