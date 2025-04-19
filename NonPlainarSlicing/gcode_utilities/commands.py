import numpy as np


class Commands:

    def __init__(self, command_array, data_list = None):

        self.command_list = command_array

        if data_list is None:
            self.count = 0
            self.capacity = 10
            self.index_for_command = np.empty(self.capacity, dtype=int)
            self.xyzef = np.empty((self.capacity, 5), dtype=float)
            self.is_mesh = np.empty(self.capacity, dtype=bool)
            return

        self.index_for_command = np.empty(len(data_list),dtype=int)
        self.xyzef = np.empty((len(data_list),5),dtype=float)
        self.is_mesh = np.empty(len(data_list),dtype=bool)


        self.index_for_command = data_list[:,0].astype(int)
        self.is_mesh = data_list[:,1].astype(bool)
        self.xyzef = data_list[:,2:].astype(float)


        self.count = len(data_list)
        self.capacity = len(data_list)

    def append(self, **params):
        if "idx" not in params:
            raise ValueError("Parameter 'idx' is required.")

        if self.count == self.capacity:
            self._resize()

        idx = params["idx"]

        if"xyzef" in params :
            self.xyzef[self.count] = params.get("xyzef",np.nan)


        else:
            x = params.get("x", np.nan)
            y = params.get("y", np.nan)
            z = params.get("z", np.nan)
            e = params.get("e", np.nan)
            f = params.get("f", np.nan)
            self.xyzef[self.count] = [x, y, z, e, f]


        is_mesh = params.get("is_mesh", np.nan)
        self.index_for_command[self.count] = idx
        self.is_mesh[self.count] = is_mesh

        self.count += 1

    def extend(self, idx: int, points: np.ndarray, f=np.nan, is_mesh=True):
        points = np.asarray(points, dtype=float)

        if points.ndim != 2 or points.shape[1] != 4:
            raise ValueError("Each point must be a list of 4 values: [x, y, z, e]")

        for x, y, z, e in points:
            self.append(
                idx=idx,
                x=x,
                y=y,
                z=z,
                e=e,
                f=f,
                is_mesh=is_mesh
            )

    def _resize(self):
        new_capacity = int(self.capacity * 1.4 + 1)
        self.xyzef = self._resize_array(self.xyzef, (new_capacity, 5))
        self.is_mesh = self._resize_array(self.is_mesh, new_capacity)
        self.index_for_command = self._resize_array(self.index_for_command, new_capacity)
        self.capacity = new_capacity

    def _resize_array(self, arr, new_shape):
        new_arr = np.empty(new_shape, dtype=arr.dtype)
        new_arr[:arr.shape[0]] = arr
        return new_arr

    def get_commands(self):
        return self.command_list

    def get_points(self):
        return self.xyzef[:self.count]

    def set_points(self, points):
        self.xyzef[:self.count] = points

    def get_command_index(self):
        return self.index_for_command[:self.count]

    def offset_points(self, offset):
        self.xyzef[:, :3] += offset

    def getValue(self, i):
        return [self.index_for_command[i], self.xyzef[i], self.is_mesh[i]]

    def override(self, commands):
        self.count = commands.count
        self.capacity = commands.capacity
        self.index_for_command = commands.index_for_command
        self.xyzef = commands.xyzef
        self.is_mesh = commands.is_mesh

        pass

    def get_string_list(self):

        print("start - to_string_list")


        out_commands = np.empty(self.count + len(self.command_list), dtype='U256')

        print(self.count)
        print(len(self.command_list))

        v_last = [-100000000, -100000000, -100000000, -100000000, -100000000]
        write_out_index = 0
        data_index = 0

        for i in range(len(self.command_list)):



            for j in range(data_index, len(self.index_for_command)):
                if self.index_for_command[j] > i:
                    data_index = j

                    break


                if self.index_for_command[j] == i:
                    final_str = ""

                    if self.command_list[i]['command'] == 'G0':
                        print("hit")

                    if self.command_list[i]['command'] == 'G1' or self.command_list[i]['command'] == 'G0':
                        v = self.xyzef[j]
                        final_str = f"{self.command_list[i]['command']}"
                        if not np.isnan(v[0]) and v_last[0] != v[0]:
                            final_str = final_str + f" X{v[0]:.2f}"
                            v_last[0] = v[0]
                        if not np.isnan(v[1]) and v_last[1] != v[1]:
                            final_str = final_str + f" Y{v[1]:.2f}"
                            v_last[1] = v[1]
                        if not np.isnan(v[2]) and v_last[2] != v[2]:
                            final_str = final_str + f" Z{v[2]:.2f}"
                            v_last[2] = v[2]
                        if not np.isnan(v[3]) and self.command_list[i]['command'] == 'G1' and v_last[3] != v[3]:
                            final_str = final_str + f" E{v[3]:.5f}"
                            v_last[3] = v[3]
                        if not np.isnan(v[4]) and v_last[4] != v[4]:
                            final_str = final_str + f" E{v[4]:.5f}"
                            v_last[4] = v[4]



                    else:
                        command_str = f"{self.command_list[i]['command']}"
                        params_str = "".join([f" {value}" for value in self.command_list[i]['parameters']])
                        final_str = command_str + params_str

                    out_commands[write_out_index] = final_str
                    write_out_index += 1

        return out_commands[:write_out_index]










