# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 22:12:51 2021
Input_File module exists to build a RASSP input file while being given all of 
the neccessary inputs

Right now, it can take a Material, Crack_Case and Nasgro object - will be expanded

@author: Cade Wooten - 3321153
"""


class Input_File(object):

    def __init__(self, material, crack_case, gen_crack_list=None,
                 job='RASSP: Test', start='SPECTRUM,SOLUTION=CRKGRO,FILE9=100,REPORT,NPRINTF',
                 spectrum='CARDS=11,RANGE,', net='1.00', mission=999, title='Title', dls='10.0', stf=''):

        self.material = material
        self.crack_case = crack_case
        self.gen_crack_list = gen_crack_list
        self.job = job
        self.start = start
        self.stf = stf
        self.spectrum = spectrum
        self.net = str(net)
        self.dls = str(dls)
        self.mission = mission
        self.title = title


    def create_input_file(self, input_file_name,
                          location='//Sw.nos.boeing.com/b1bdata/data300$/groups/structures_3/users_data/Wooten'
                                   '/00_Tools/RASSP_Automation/Sandbox/'):
        input_string_list = []

        # The first part of the input file, will likely be expanded later
        input_string_list.append('$JOB ' + self.job)
        input_string_list.append('$START=' + self.start)
        if self.stf != '':
            input_string_list.append(self.stf)
        input_string_list.append('$SPECTRUM=' + self.spectrum)
        input_string_list.append(f'$NET=(-1.00,-{self.net},0.0,0.0,1.00,{self.net}),')
        input_string_list.append(f'$MISSION={self.mission}')
        input_string_list.append('TITLE')
        input_string_list.append(self.title)
        input_string_list.append('END')

        # MATERIAL Section
        input_string_list.append(self.material.input_file_format())

        # Crack case / code section
        input_string_list.append(self.crack_case.input_file_format())

        if self.crack_case.code == '1080' or self.crack_case.code == '2080':
            num_betas = 0
            # Get total number of Betas, combine the CC and TC lists
            for gen_crack in self.gen_crack_list:
                num_betas = num_betas + gen_crack.get_num_betas()

            input_string_list.append('EDGE CRACK')  # ie: EDGE CRACK

            # Thru thickness values not needed for 2080
            if self.crack_case.code == '1080':
                # Hard coded values used for this... usual procedure I have followed
                input_string_list.append('02'.rjust(10))
                input_string_list.append('0.0025'.rjust(10) + '1.0000'.rjust(10))
                input_string_list.append('0.0050'.rjust(10) + '1.0000'.rjust(10))

            input_string_list.append(str(num_betas).rjust(10))  # total numer of Betas,Required for input file

            # Loop through all beta parameters in the gen_crack list
            for gen_crack in self.gen_crack_list:
                input_string_list.append(gen_crack.beta_input_file_format())

        # Ending seciton. Subject to change or expansion
        input_string_list.append('1'.rjust(10) + self.dls.rjust(10))

        input_string_list.append('OUTPUT')
        input_string_list.append('    0 2000    0                        0')

        input_string_list.append('END DATA')
        input_file_string = '\n'.join(input_string_list)

        input_file = open(location + input_file_name, 'w', encoding='utf-8')
        input_file.write(input_file_string)

    """
    
    """

    @staticmethod
    def mod_input_crack_size(base_input_file_name, flaw_sizes_a, flaw_sizes_c, remove_base=False, limit_a='',
                             limit_c='',
                             location='//Sw.nos.boeing.com/b1bdata/data300$/groups/structures_3/users_data/Wooten'
                                      '/00_Tools/RASSP_Automation/Sandbox/'):
        import os, glob
        os.chdir(location)

        flaw_sizes_a.sort()
        flaw_sizes_c.sort()

        flaw_size_a = flaw_sizes_a[0]
        flaw_size_c = flaw_sizes_c[0]

        # Grab any files in the current directory that contain the base input file name and a .input extension
        input_files = glob.glob(f"*{base_input_file_name}*.input")

        # The program will read the first file in the list
        input_file = location + input_files[0]
        base_input_file = open(input_file, 'r')

        lines = base_input_file.readlines()
        base_input_file.close()
        if remove_base == True:
            os.remove(input_file)
        limits_index = 0
        for i in range(len(lines)):
            if 'LIMITS' in lines[i]:
                limits_index = i + 1

        mod_lines = lines.copy()
        limits_string = mod_lines[limits_index]
        limits_string_split = limits_string.split()
        if len(limits_string_split) < 6:
            limits_string_split.insert(1, limit_a)
            limits_string_split.insert(3, limit_a)

        limits_string_split[0] = str(flaw_size_a)
        limits_string_split[1] = str(limit_a)
        limits_string_split[2] = str(flaw_size_c)
        limits_string_split[3] = str(limit_c)
        limits_string_split[4] = str(limits_string_split[4])
        limits_string_split[5] = str(limits_string_split[5])
        mod_lines[limits_index] = (limits_string_split[0].rjust(10) + limits_string_split[1].rjust(10) +
                                   limits_string_split[2].rjust(10) + limits_string_split[3].rjust(10) +
                                   limits_string_split[4].rjust(10) + limits_string_split[5].rjust(10) + '\n')

        current_input_file_name = base_input_file_name + '.input'
        current_input_file = open(location + current_input_file_name, 'w')
        current_input_file.writelines(mod_lines)
        current_input_file.close()
