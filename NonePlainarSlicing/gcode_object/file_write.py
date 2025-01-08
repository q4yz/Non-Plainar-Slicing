
import numpy as np

def printTofile( commandList, pointsIndex, pointList):
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