
import numpy as np

def printTofile( commandList, pointsIndex, pointList):
        print("start - printTofile")
        outCommands = np.empty(len(commandList) + len(pointList), dtype='U256')
        print(len(pointsIndex))
        print(len(pointList))
        pointsIndex_reshaped = pointsIndex.reshape(-1, 1)
        indexPointList = np.hstack([pointsIndex_reshaped, pointList])
        v_last = [-1,-1,-1,-1]
        commandWriteIndex = 0
        for i , c in enumerate(commandList):
        
            if c['command'] == 'G1' :

                mask = indexPointList[:,0] == i
                sub = indexPointList[mask]

                for v in sub:
                    #if not np.isnan(v[4])and v_last[3] != v[4]:
                    final_str = f"{c['command']}"
                    if not np.isnan(v[1]) and v_last[0] != v[1]:
                        final_str = final_str + f" X{v[1]:.2f}"
                        v_last[0] = v[1]
                    if not np.isnan(v[2])and v_last[1] != v[2]:
                        final_str = final_str + f" Y{v[2]:.2f}"
                        v_last[1] = v[2]
                    if not np.isnan(v[3])and v_last[2] != v[3]:
                        final_str = final_str + f" Z{v[3]:.2f}"
                        v_last[2] = v[3]
                    if not np.isnan(v[4])and v_last[3] != v[4]:
                        final_str = final_str + f" E{v[4]:.5f}"
                        v_last[3] = v[4]
                    
                     
                    outCommands[commandWriteIndex] = final_str
                    commandWriteIndex +=1

            elif  c['command'] == 'G0':

                mask = indexPointList[:,0] == i
                sub = indexPointList[mask]

                for v in sub:
                    final_str = f"{c['command']}"
                    if not np.isnan(v[1]):
                        final_str = final_str + f" X{v[1]:.2f}"
                    if not np.isnan(v[2]):
                        final_str = final_str + f" Y{v[2]:.2f}"
                    if not np.isnan(v[3]):
                        final_str = final_str + f" Z{v[3]:.2f}"
                   
                    
                     
                    outCommands[commandWriteIndex] = final_str
                    commandWriteIndex +=1

            else:
                command_str = f"{c['command']}"
                params_str = "".join([f" {value}" for  value in c['parameters']])    
                final_str = command_str + params_str

                outCommands[commandWriteIndex] = final_str
                commandWriteIndex +=1
            
        outCommands = outCommands[:commandWriteIndex]
        
  
        file_path = "C:\Daten\Test-Slicer\Gcode_OUT\out.gcode"
        export(file_path, outCommands)

def export ( path, outCommands):
    
    try:
        with open(path, 'w') as file:
            for command in outCommands:
                file.write(command + '\n')
    except Exception as e:
        print(f"Error writing to file: {e}")
    else:
        print("File written successfully.")

    print("end - printTofile")