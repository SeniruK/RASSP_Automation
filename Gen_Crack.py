# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 17:33:33 2021

This module exists to automate the NASSIF program (NASGRO) by taking the required
inputs from the user and creating a batch file to be run by NASGRO via the command line 

See the NASGRO documentation for details on the batch file format and execution procedure

Currently Only supports crack cases CC16 and TC03 - intend to expand

The user will input all of the required data for the desired crack case (geometry, loads, material props, crack sizes)
The program will run in the background and the K1 and Beta values can be extracted 
through the use of class methods

Much like the material class, the beta value array can be formatted and returned as a string 
to match required RASSP input file format 


@author: Cade Wooten - 3321153
"""
from textwrap import dedent

class Gen_Crack(object):

    # Constructor
    def __init__(self):

        self.k_vals_array = []
        self.beta_vals_array = []
        self.num_betas = 0

    # =============================================================================
    #   Method that will run nassif in the background by creating the appropriate batch file and running it
    #   Then retrieving the K_vals from the appropriate file
    # =============================================================================
    def run_nassif(self, kind, config_name, crack_code, geometry, stresses, mat_props, crack_sizes_a, crack_sizes_c,
                   k_choice='K_ave', num_cracks=1):
        self.crack_code = crack_code
        self.geometry = geometry.copy()
        self.stresses = stresses.copy()
        self.mat_props = mat_props
        self.config_name = config_name
        self.crack_sizes_c = crack_sizes_c.copy()
        self.crack_sizes_a = crack_sizes_a.copy()
        self.kind = kind
        self.k_choice = k_choice
        self.num_cracks = num_cracks

        self.create_batch_file()
        self.execute_batch_file()
        self.extract_k_vals()

    # =============================================================================
    #   This is going to get pretty messy.
    #   Creates the batch file for nassif input
    # =============================================================================
    def create_batch_file(self):

        # Common data for all cases
        header_string = dedent(f"""\
                            {self.config_name}
                            1
                            [no title given]
                            {self.crack_code['type']}
                            {self.crack_code['number']}
                            """)
        # Group all of the geometry together for different cases
        geometry_string = self.get_geometry_string()

        # another block of common text
        output_options_string = dedent("""
                                0    		[compounding option]
                                S    		[compute SIF]
                                """)
        # Group the stress output together, varies for different cases
        stresses_string = self.get_stresses_string()

        # Get the crack sizes that have been formatted
        crack_sizes_string = self.get_crack_sizes_string()

        # Open (create) the batch
        # TODO change this to server location
        # f = open('//Sw.nos.boeing.com/b1bdata/data300$/groups/structures_3/users_data/Wooten/Tools/RASSP_Automation/NASSIF/'+self.config_name+'.SIFBAT', 'w+')
        f = open(
            'C:/Users/ze273f/Desktop/RASSP_Automation/NASSIF/' + self.config_name + '.SIFBAT',
            'w+')
        f.write(header_string + geometry_string + output_options_string + stresses_string
                + crack_sizes_string)
        f.close()

    # =============================================================================
    #   Helper function to format the geometry section for the batch file
    #   The format for a corner crack vs thru crack differs slightly
    # =============================================================================
    def get_geometry_string(self):
        geometry_string = ""

        # If it is a corner crack
        if self.crack_code['type'] == 'CC' and (self.crack_code['number'] == 16):
            geometry_string = dedent(f"""\
                                     {self.num_cracks}       [Crack QTY]
                                     {self.geometry['t']}       [Thickness, t]
                                     {self.geometry['W']}      [Width, W]
                                     {self.geometry['D']}      [Hole Diameter, D]""")
            if self.num_cracks == 1:
                geometry_string += ("\n" + self.geometry['B'] + "      [Hole ctr offset, B]")
        # If it is a thru crack
        if self.crack_code['type'] == 'TC' and (self.crack_code['number'] == 3):
            geometry_string = dedent(f"""\
                                     {self.geometry['W']}      [Width, W]
                                     {self.geometry['t']}       [Thickness, t]
                                     {self.geometry['D']}      [Hole Diameter, D]
                                     {self.geometry['B']}      [Hole ctr offset, B]""")

            # If it is a thru crack
        if self.crack_code['type'] == 'TC' and (self.crack_code['number'] == 5):
            geometry_string = dedent(f"""\
                                     {self.geometry['t']}       [Thickness, t]
                                     {self.geometry['D']}      [Hole Diameter, D]
                                     {self.geometry['W']}      [Hole ctr spacing, W/H]
                                     0         [D/B (0 if S0 applied)]
                                     {self.num_cracks}          [Crack QTY]""")
        return geometry_string

    # =============================================================================
    #   Helper function to format the stress section for the batch file
    #   The format for a corner crack vs thru crack differs slightly
    # =============================================================================
    def get_stresses_string(self):
        stresses_string = ""
        if (self.crack_code['type'] == 'CC' and (self.crack_code['number'] == 16)):
            stresses_string = dedent(f"""\
                                     {self.stresses['S0']}
                                     {self.stresses['S1']}
                                     {self.stresses['S3']}
                                     """)
        if (self.crack_code['type'] == 'TC' and (self.crack_code['number'] == 3)):
            stresses_string = dedent(f"""\
                                     {self.stresses['S0']}
                                     {self.stresses['S1']}
                                     {self.stresses['S2']}
                                     {self.stresses['S3']}
                                     """)

        if (self.crack_code['type'] == 'TC' and (self.crack_code['number'] == 5)):
            stresses_string = dedent(f"""\
                                     {self.stresses['S0']}
                                     {self.stresses['S3']}
                                     {self.stresses['S4']}
                                     """)
        return stresses_string

    # =============================================================================
    #   Helper function to format the crack size list
    # =============================================================================
    def get_crack_sizes_string(self):
        # Start with empty list of strings that will added to in parts - each entry = 1 line
        join_strings_list = []
        join_strings_list.append(f"{self.mat_props['Fty']}    		[material yield stress]")
        join_strings_list.append("T    		[tabulate solution]")

        # loop through the crack sizes list
        for i in range(len(self.crack_sizes_a)):
            join_strings_list.append(str(self.crack_sizes_a[i]))  # add the current size to the list

            # If the crack is a corner crack,also add the length direction size
            if (self.crack_code['type'] == 'CC'):
                join_strings_list.append(str(self.crack_sizes_c[i]))

        # Random values needed for batch file
        join_strings_list.append("-1\n0 \n0\n")

        # Join the string list into one string with newline separating them
        return "\n".join(join_strings_list)

    # =============================================================================
    #   Method to actually run the NASSIF program
    # =============================================================================
    def execute_batch_file(self):
        import subprocess, os
        # Nassif batch files have to be stored in a very particular location.
        # TODO update this location if this is ever distributed
        os.chdir("C:/Users/ze273f/Desktop/RASSP_Automation/NASSIF/")

        # Subprocess to run the  batch file, emulates a cmd prompt
        subprocess.Popen(
            f"C:/Users/ze273f/Desktop/RASSP_Automation/NASSIF/helper4.exe nasfla4 {self.config_name}.sifbat 3",
            shell=True).wait()

    # =============================================================================
    #   Method to extract the K values array from the output file
    # =============================================================================
    def extract_k_vals(self):
        import os
        # TODO change this for distribution
        os.chdir("C:/Users/ze273f/Desktop/RASSP_Automation/NASSIF/")
        batch_output = open(f"{self.config_name}", "r")  # open the output file in read mode

        k_choice = self.k_choice

        # loop through output file line by line
        for line in batch_output:
            if "|" in line:  # If the line contains pipe character (where the results go in the NASSIF output)
                k_list = []  # Initialize the list of K values

                # Loop through the line and append only the numberical values
                for char in line.split():
                    try:
                        k_list.append(float(char))
                    except ValueError:
                        pass

                if len(k_list) < 1:  # If the list is empty (no numberical values) -> ignore it
                    continue

                # If number of values is over 6, get rid of the first one
                # This is going to be the a/c value of 1 for a CC
                if (len(k_list) > 6):
                    k_list.pop(0)
                k_list.pop(len(k_list) - 1)  # Remove the last element (Sn/Sy)
                k_list.pop(len(k_list) - 1)  # Remove the new last element (Sn)

                # Indicates the output file is for a CC case
                if (len(k_list) >= 4):
                    k_list.pop(0)  # Remove the first element (a) - we just need c


                else:  # Must have been a TC case

                    k_list.append(k_list[1])  # Duplicate the K(c) value

                if k_choice == 'K_a':
                    k_ave = .5 * (k_list[1] + k_list[1])

                if k_choice == 'K_c':
                    k_ave = .5 * (k_list[2] + k_list[2])

                if k_choice == 'K_ave':
                    k_ave = .5 * (k_list[1] + k_list[2])  # Find the average K val
                k_list.append(round(k_ave * 1000, 1))  # append the average k val *1000

                self.k_vals_array.append(k_list)  # Append this line to the full K_vals array
        batch_output.close()  # Close the output file

    # =============================================================================
    #   Method to set the K_vals of the class. Will take in a list of crack sizes and a list of k_vals
    #   It is assumed that the user will do any cleanup needed for the k_vals (average, multiply by 1000 etc.)
    # =============================================================================
    def set_k_vals(self, crack_lengths_list, k_vals_list):
        self.k_vals_array = []

        for i in range(len(k_vals_list)):
            a = float(crack_lengths_list[i])
            k = float(k_vals_list[i])

            # Insert the crack length and then the k_val three times
            # This is because the calc_betas function is set up to take a nasgro type k_vals
            # whcih has Ka, Kc, and Kave
            temp_list = [a, '-', '-', k]

            # Append the current temp_list to the array of K_vals
            self.k_vals_array.append(temp_list)

    # =============================================================================
    #   Method to set the Beta values of the class
    #   Similar to the set_k_vals method, it will just take in a list of crack sizes
    #   and beta values. In this case the entire beta array outside of the first column (crack sizes)
    #   will be filled with the same beta values (no need for k_vals if we already have betas)
    # =============================================================================
    def set_betas(self, crack_lengths_list, betas_list):
        self.beta_vals_array = []

        # Loop through the list of betas to add them all to a temp array (list)
        for i in range(len(betas_list)):
            a = float(crack_lengths_list[i])
            beta = float(betas_list[i])

            temp_list = [a, '-', '-', '-', beta]

            self.beta_vals_array.append(temp_list)

    # =============================================================================
    #   Uses the K_vals array and a far field stress to calculate the beta gradient
    #   I got this formula from Jared Yunk's RASSP_INPUT excel tool
    # =============================================================================
    def calc_betas(self, far_field, geometry, crack_case='1080'):
        import math
        self.beta_vals_array = self.k_vals_array.copy()

        far_field = float(far_field) * 1000
        # Loop through the beta array one line at a time to add the beta to the array
        for k_step in self.beta_vals_array:

            a = k_step[0]  # First value in the list is the crack length (a)
            k = k_step[3]  # The average k_val

            # Geometric parameters needed for calc
            t = float(geometry['t'])
            a_div_t = a / t
            part = a < t  # If the current line is for a part thru crack

            # List of parameters needed for beta calculation default to thru crack values
            q = (1 + 1.464)
            term_1 = 1
            term_2 = (math.pi * (a)) ** (0.5)
            beta = (k) / (far_field * term_2)

            # If it is a part thru crack, change the values
            if part and crack_case != '2080':
                term_1 = ((1.13 - 0.09 * 1) + (((0.89 / (0.2 + 1)) - (0.54)) * (a_div_t) ** 2) +
                          (((.5) - (1 / (0.65 + 1)) + (14) * (1 - 1) ** 24) * (a_div_t) ** 4))
                term_2 = (math.pi * (a / q)) ** (0.5)
                beta = (k) / (term_1 * term_2 * far_field)

            k_step.append(round(beta, 4))  # Append the beta value to the k_vals array entry
        self.num_betas = len(self.beta_vals_array)

    # =============================================================================
    #   Returns a string representation of the array of crack size, k, and beta values
    # =============================================================================
    def get_summary_array(self):
        # Going to piece together the output string as a list then join at the end
        summary_string_list = []

        # Step through the beta vals array one line at a time
        # Each line contains the crack size and corresponding k and beta values
        for var_list in self.beta_vals_array:
            a = str(var_list[0])
            k1 = str(var_list[1])
            k2 = str(var_list[2])
            kave = str(var_list[3])
            beta = str(var_list[4])

            # Append the string representation to the list of strings
            summary_string_list.append(a.rjust(10) + k1.rjust(10) + k2.rjust(10) + kave.rjust(10) + beta.rjust(10))

        # Join the string list into one return string
        input_file_string = '\n'.join(summary_string_list)
        return input_file_string

    def get_num_betas(self):
        return self.num_betas

    # =============================================================================
    #    Return the beta values formatted for a rassp .input file
    # =============================================================================
    def beta_input_file_format(self):

        # Piece together the return string as list of individual lines and then join at the end
        beta_string_list = []

        # Loop through beta array line by line
        for beta_val_list in self.beta_vals_array:
            a = str(beta_val_list[0])
            beta = str(beta_val_list[4])
            beta_string_list.append(a.rjust(10) + beta.rjust(10))

        input_file_string = '\n'.join(beta_string_list)
        # print(self.get_summary_array())
        return input_file_string

    # =============================================================================
    #   Method to return a value for crack depth using a given value for crack length
    #   and an existing k_vals_array
    #   2D Method
    # =============================================================================
    def calc_a_1(self, a_0, c_0, c_1, Nu):
        for entry in self.k_vals_array:

            if (entry[0] == float(c_0)):
                k_a = entry[1]
                k_c = entry[2]
                term_1 = (k_c / k_a) ** float(Nu)
                a_1 = (c_1 - c_0) / (term_1) + a_0
                return round(a_1, 4)
            else:
                pass

    @staticmethod
    def write_to_file(windows_dir, base_file_name, gen_crack_list):
        import os

        if not os.path.isdir(windows_dir + "SIF_Calculations"):
            os.mkdir(windows_dir + "SIF_Calculations/")
        sif_output = open(windows_dir + "SIF_Calculations/SIF_Calc_" + base_file_name + '.txt', 'w')

        sif_output.write(
            'a'.rjust(10) + 'K_a'.rjust(10) + 'K_c'.rjust(10) + 'K_avg'.rjust(10) + 'Beta'.rjust(10) + '\n')
        for gen_crack in gen_crack_list:
            sif_output.write(gen_crack.get_summary_array() + '\n')

        sif_output.close()
