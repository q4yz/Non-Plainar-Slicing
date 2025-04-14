
import numpy as np
#from ..globals import Glob

from NonPlainarSlicing.globals  import Glob

def to_gcode_list(command_list, points_index, point_list):
        print("start - printTofile")
        out_commands = np.empty(len(command_list) + len(point_list), dtype='U256')
        print(len(points_index))
        print(len(point_list))
        points_index_reshaped = points_index.reshape(-1, 1)
        index_point_list = np.hstack([points_index_reshaped, point_list])
        v_last = [-1,-1,-1,-1]
        command_write_index = 0


        Glob.initialize_progress_2(len(command_list))


        for i , c in enumerate(command_list):
            Glob.progressed_2()
            if c['command'] == 'G1' :

                mask = index_point_list[:,0] == i
                sub = index_point_list[mask]

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
                    
                     
                    out_commands[command_write_index] = final_str
                    command_write_index +=1

            elif  c['command'] == 'G0':

                mask = index_point_list[:,0] == i
                sub = index_point_list[mask]

                for v in sub:
                    final_str = f"{c['command']}"
                    if not np.isnan(v[1]):
                        final_str = final_str + f" X{v[1]:.2f}"
                    if not np.isnan(v[2]):
                        final_str = final_str + f" Y{v[2]:.2f}"
                    if not np.isnan(v[3]):
                        final_str = final_str + f" Z{v[3]:.2f}"
                   
                    
                     
                    out_commands[command_write_index] = final_str
                    command_write_index +=1

            else:
                command_str = f"{c['command']}"
                params_str = "".join([f" {value}" for  value in c['parameters']])    
                final_str = command_str + params_str

                out_commands[command_write_index] = final_str
                command_write_index +=1
            
        out_commands = out_commands[:command_write_index]
        
  
        
        
        #export(file_path, outCommands)
        
        Glob.set_progress2(1)
        return out_commands

def export (path, out_commands):
    
    try:
        with open(path, 'w') as file:
            for command in out_commands:
                file.write(command + '\n')
    except Exception as e:
        print(f"Error writing to file: {e}")
    else:
        print("File written successfully.")

    print("end - printTofile")