

import numpy as np
from NonPlainarSlicing.globals  import Glob
def readGcodeFileToDicList( file_path) -> list[None] | None:
    print("start - read_gcode")

    try:
        instructions = []
        i = 0
        with open(file_path, 'r') as file:
            
            lines = file.readlines()  # Read all lines into a list
            instructions = [None] * len(lines)  # Create a list of None with the same length

            Glob.initialize_progress(len(lines))
            
            for line in lines:

                Glob.progressed()


                if not line:
                    continue

                tokens = line.split()
                if tokens:
                    instruction = {'command': tokens[0], 'parameters': {}}
                    if tokens[0] == "G0" or tokens[0] =="G1":
                        for token in tokens[1:]:
                            try:
                                if len(token) > 1:
                                    instruction['parameters'][token[0]] = float(token[1:])
                            except ValueError:
                                pass
                    else:
                        instruction['parameters'] = []
                        for token in tokens[1:]:
                            
                            instruction['parameters'].append(token)

              
                    instructions[i] = instruction
                    i += 1

        instructions = instructions[:i]
        
        print("end - read_gcode")
        
        #print(instructions)
        return instructions # , combined
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error reading file: {e}")
    return None


