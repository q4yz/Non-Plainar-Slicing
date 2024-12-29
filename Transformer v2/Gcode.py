from textwrap import indent
from time import sleep
import tkinter as tk
import tkinter
from tkinter import filedialog
from tkinter import ttk
import numpy as np
import mesh_object
from Constants import *

class Gcode():
    outCommands = []

    def __init__(self, path, meshobject) -> None:
        
        #path = r'C:\Daten\Test-Slicer\Gcode_IN\CFFFP_out.gcode'

        commandList, boundingBox = self.read_gcode(path)
        commandListidexOfPoints, commandListPoints = self.getPointsFromCommands(commandList)
        commandListidexOfPoints, commandListPoints = self.segmentizeLines(commandListidexOfPoints, commandListPoints, 0.5)

        print("bounding" + str(boundingBox))

        min_values = boundingBox[0]
        max_values = boundingBox[1]
        center = min_values + (max_values - min_values)/2
        offset = np.array((center[0],center[1],0))  #min_values[2]

       
        self.shiftPoints(commandListPoints, -offset )

        commandListPoints = self.zBackTrans(commandListPoints, meshobject)

        
        self.shiftPoints(commandListPoints, offset )
        
        self.printTofile(commandList, commandListidexOfPoints, commandListPoints )

    pass
    def read_gcode(self, file_path):
        print("start - read_gcode")
        try:
            with open(file_path, 'r') as file:
                instructions = []
                min_coords = {'X': float('inf'), 'Y': float('inf'), 'Z': float('inf')}
                max_coords = {'X': float('-inf'), 'Y': float('-inf'), 'Z': float('-inf')}

                for line in file:
                    # Remove comments and whitespace
                    line = line.split(';')[0].strip()
                    if not line:
                        continue

                    
                    tokens = line.split()
                    if tokens:
                        instruction = {'command': tokens[0], 'parameters': {}}
                        for token in tokens[1:]:
                            try:
                                if len(token) > 1:
                                    instruction['parameters'][token[0]] = float(token[1:])
                            except ValueError:
                                # Skip non-numeric tokens
                                pass
                        

                        if instruction['command'] == 'G1' :
                            for axis in 'XYZ':
                                if axis in instruction['parameters']:
                                    value = instruction['parameters'][axis]
                                    min_coords[axis] = min(min_coords[axis], value)
                                    max_coords[axis] = max(max_coords[axis], value)

                        instructions.append(instruction)



            minArr = np.array(list(min_coords.values()))
            maxArr = np.array(list(max_coords.values()))

            # Combine into a single array
            combined = np.vstack((minArr, maxArr))
            print("end - read_gcode")
            return instructions, combined
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"Error reading file: {e}")
        

    def getPointsFromCommands(self, commandList):
        print("start - getPointsFromCommands")
        commandListPoints = np.empty((len(commandList), 4))  # Pre-allocate the array
        commandListidexOfPoints = np.empty(len(commandList), dtype=int)

        point_count = 0 

        for idx, command in enumerate(commandList):
            if command['command'] == 'G1' or command['command'] == 'G0':  # Select only G1 commands
                params = command.get('parameters', {})
                x = params.get('X', None)
                y = params.get('Y', None)
                z = params.get('Z', None)  
                e = params.get('E', None)  
                commandListPoints[point_count] = [x, y, z, e]
                commandListidexOfPoints[point_count] = idx

                point_count += 1 

        commandListPoints = commandListPoints[:point_count]
        commandListidexOfPoints = commandListidexOfPoints[:point_count]
        print("end - getPointsFromCommands")
        return commandListidexOfPoints, commandListPoints

    def segmentizeLines(self, pointsIndex,pointList, threshold  ):
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

    def shiftPoints(self, points, offset):
        offset = np.append(offset, 0)
        points[:, :4] += offset


    def zBackTrans(self, commandListPoints, mesh:mesh_object.MeshObject):
        print("start - zBackTrans")
        locations, index_ray = mesh.distortOnTrans(commandListPoints[:,:3])

        np.set_printoptions(precision=4, suppress=True, edgeitems=8)  
   
        commandListPoints[index_ray, 2] = commandListPoints[index_ray, 2] -  locations[:, 2]
        print("end - zBackTrans")
        return commandListPoints



    def printTofile(self, commandList, pointsIndex, pointList):
        print("start - printTofile")
        outCommands = np.empty(len(commandList) + len(pointList), dtype='U256')
        print(len(pointsIndex))
        print(len(pointList))
        pointsIndex_reshaped = pointsIndex.reshape(-1, 1)
        indexPointList = np.hstack([pointsIndex_reshaped, pointList])

        commandWriteIndex = 0
        for i , c in enumerate(commandList):
        
            if c['command'] == 'G1' or c['command'] == 'G0':

                mask = indexPointList[:,0] == i
                sub = indexPointList[mask]

                for v in sub:
                    final_str = f"{c['command']} X{v[1]:.2f} Y{v[2]:.2f} Z{v[3]:.2f} E{v[4]:.2f}"
                    outCommands[commandWriteIndex] = final_str
                    commandWriteIndex +=1

            else:
                command_str = f"{c['command']}"
                params_str = "".join([f" {key}{value}" for key, value in c['parameters'].items()])    
                final_str = command_str + params_str

                outCommands[commandWriteIndex] = final_str
                commandWriteIndex +=1
            
        outCommands = outCommands[:commandWriteIndex]
        
        self.outCommands = outCommands


        file_path = "C:\Daten\Test-Slicer\Gcode_OUT\out.gcode"
        self.export(file_path)

    def export (self, path):
        outCommands = self.outCommands
        try:
            with open(path, 'w') as file:
                for command in outCommands:
                    file.write(command + '\n')
        except Exception as e:
            print(f"Error writing to file: {e}")
        else:
            print("File written successfully.")

        print("end - printTofile")

  



