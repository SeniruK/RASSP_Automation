# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 12:27:57 2021

This module serves as a way for other programs to interact with the RASSP materials list

The main function of the MaterialList class is to read through the material input file 
and set the intance variable (list) master_material_list The materials in the list are 
indexed which will make any filerting of the list easier. (ie. If the user wishes to only display Alum values)

The Material object encapsulates all of the data for each material into one class
The material class has a method to output a string in the format needed for a
RASSP input file

@author: Cade Wooten - 3321153
"""

test_val = 10


class Material(object):

    def __init__(self, params):

        # Pretty self explanitory, set all of the material variables to the values passed in
        # Keep in mind these can always be accessed as a dictionary thorugh the vars(object) function
        self.mat_name = params['mat_name']
        self.prod_form = params['prod_form']
        self.temper = params['temper']
        self.Fty = str(round(float(params['Fty']), 1))
        self.procure_spec = params['procure_spec']
        self.Kc = str(round(float(params['Kc']), 1))
        self.environment = params['environment']
        self.Cu = params['Cu']
        self.Nu = params['Nu']
        self.Mu = params['Mu']
        self.Qu = params['Qu']
        self.Cl = params['Cl']
        self.Nl = params['Nl']
        self.Ml = params['Ml']
        self.Ql = params['Ql']
        self.Rp = params['Rp']
        self.Rm = params['Rm']
        self.Rso = params['Rso']
        self.trans_k = params['trans_k']
        self.trans_daDn = params['trans_daDn']
        self.Ktho = params['Ktho']
        self.mat_index = params['mat_index']
        self.orientation = params['orientation']
        self.grade = params['grade']
        self.MAT_ID = self.mat_name + " " + self.temper + " " + self.prod_form + " " + self.environment
        self.bislope = True
        self.params = params

    # Kc needs its own setter. That is the parameter that can vary the most and is not tabulated (as of yet)
    def set_Kc(self, Kc):
        if Kc == '':
            self.Kc = str(round(float(self.params['Kc']), 1))
        else:
            Kc_float = round(float(Kc), 1)
            self.Kc = str(Kc_float)

    # String representation of material. Allows it to be passed directly to a print() function
    def __str__(self):
        return (self.mat_name)

    # Format the material data for the RASSP .input file
    def input_file_format(self):
        material_string_list = []
        material_string_list.append('MATERIAL')
        if self.bislope:
            material_string_list.append(self.MAT_ID.ljust(60) + 'BISLOPE')
        else:
            material_string_list.append(self.MAT_ID.ljust(60))
        material_string_list.append(self.Cu.rjust(10) + self.Nu.rjust(10) + self.Cu.rjust(10) + self.Nu.rjust(10)
                                    + self.Mu.rjust(10) + self.Qu.rjust(10))
        if self.bislope:
            material_string_list.append(self.Cl.rjust(10) + self.Nl.rjust(10) + self.Cl.rjust(10) + self.Nl.rjust(10)
                                        + self.Ml.rjust(10) + self.Ql.rjust(10) + self.trans_k.rjust(
                5) + self.trans_daDn.rjust(5))
        material_string_list.append(self.Kc.rjust(10) + self.Kc.rjust(10) + self.Fty.rjust(10))
        material_string_list.append('THRESHOLD')
        material_string_list.append(self.Ktho.rjust(10) + '0'.rjust(10))
        # material_string_list.append()
        input_file_string = '\n'.join(material_string_list)
        return input_file_string


class Material_List:

    def __init__(self,
                 path='//Sw.nos.boeing.com/b1bdata/data300$/groups/structures_3/users_data/Wooten/00_Tools/RASSP_Automation/Util/Material List.xlsx'):
        self.path = path
        self.master_material_list = []
        self.current_material_list = []

        # Use pandas dataframe to input material data from excel
        # dtype = str allows pandas to read all inputs as a string
        # Helps with formatting output of material properties for input files
        import pandas as pd
        material_data = pd.read_excel(self.path, dtype=str)

        # the headers of the excel file, need to match the parameters of the Material class
        parameter_names = list(material_data)

        # The dictionary that will be used to construct the individual material objects
        material_constructor_params = {}

        # Loop through data frame one row at a time
        for mat_index in material_data.index:

            # Set the material ID to the current row (Not really needed but may be nice later) *it was nice later*
            material_constructor_params['mat_index'] = mat_index

            # Loop through all of the different parameters that are stored in parameter_names
            for param in parameter_names:
                # Add the current parameter value for this row to the material constructor dictionary
                material_constructor_params[param] = material_data[param][mat_index]

            # Create a new material object and pass in the data for current row
            new_material = Material(material_constructor_params)

            # Add the material to the master material list
            self.master_material_list.append(new_material)
        self.current_material_list = self.master_material_list.copy()

    # =============================================================================
    #     Pretty cool little function
    #     Filters the data based on a dictionary of parameters provided by the user
    #     Stores the filtered list in the currenet materials list instance variable
    # =============================================================================
    def filter_materials(self, params):
        for search_param in params:
            self.current_material_list = list(filter(lambda material: (vars(material)[search_param] ==
                                                                       params[search_param]),
                                                     self.current_material_list))

        return self.current_material_list.copy()

    def reset(self):
        self.current_material_list = self.master_material_list.copy()

    # Gives the ability to access like an array - material_list[0]
    def __getitem__(self, item):
        return self.master_material_list[item]

    # Return the length of the material list (Num materials)
    def get_length(self):
        return len(self.master_material_list)

    # Return the master list of all materials - will be helpful for the GUI
    def get_master_list(self):
        return self.master_material_list.copy()

    def get_current_list(self):
        return self.current_material_list.copy()
