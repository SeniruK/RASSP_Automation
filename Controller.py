# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 13:20:43 2021
@author: Cade Wooten - 3321153
"""

import Material, Input_File, RASSP, Gen_Crack, Crack_Case, Process_Output
import os
from textwrap import dedent


class Controller(object):

    def __init__(self):

        self.crack_case_selected = None
        self.rassp_install_location = os.getcwd().replace("\\", '/') + '/'

        self.material_list = Material.Material_List()
        self.mat_view = None
        self.input_view = None

        self.mat_filter_combobox_lists = {}

        self.text_input_values = {}
        self.checkbox_input_values = {}
        self.combobox_input_values = {}
        self.radiobutton_input_values = {}
        self.rassp = None
        self.crack_case = None
        self.input_file = None

        self.gen_crack_list = []

        self.gen_crack_selected = ''

        # These material filters need to have the same name as the variable names in the material class
        self.mat_filters = ['mat_name', 'prod_form', 'temper', 'grade', 'procure_spec', 'orientation']
        self.mat_filter_titles = ['Material Name', 'Form', 'Temper', 'Grade', 'Procurement Spec', 'Orientation']
        self.filter_title_map = dict(zip(self.mat_filters, self.mat_filter_titles))

        # TODO change all of this to read a text file, will make adding crack cases much easier
        self.crack_cases = {
            '1010': {'W': 'Width', 't': 'Thickness'},
            '1020': {'W': 'Width', 't': 'Thickness', 't2': 'Thickness 2'},
            '1030': {'W': 'Width', 't': 'Thickness', 'D': 'Diameter', 'B': 'Edge Distance'},
            '1040': {'W': 'Width', 't': 'Thickness', 'D': 'Diameter'},
            '1050': {'W': 'Width', 't': 'Thickness', 'D': 'Diameter'},
            '1060': {'W': 'Width', 't': 'Thickness', 'D': 'Diameter', 'B': 'Edge Distance', 'lt': 'LT%'},
            '1070': {'W': 'Width', 't': 'Thickness'},
            '1080': {'W': 'Width', 't': 'Thickness', 'D': 'Diameter', 'B': 'Edge Distance'},
            '2080': {'W': 'Width', 't': 'Thickness', 'D': 'Diameter', 'B': 'Edge Distance'}
        }

        self.crack_cases_titles = {'1010': 'Surface Crack',
                                   '1020': 'Embedded Crack',
                                   '1030': 'Open Hole 1 Corner Crack',
                                   '1040': 'Open Hole Mid Crack',
                                   '1050': 'Open Hole 2 Corner Cracks',
                                   '1060': 'Open Hole 1 Corner Crack',
                                   '1070': 'Surface Edge Crack',
                                   '1080': 'Generalized Part-Thru Crack',
                                   '2080': 'Generalized Thru Crack'
                                   }

        self.gen_crack_text_options = {'S0': 'S0',
                                       'S1': 'S1',
                                       'S2': 'S2',
                                       'S3': 'S3',
                                       'S4': 'S4',
                                       'far_field': 'Far Field',
                                       'cc_soln': 'CC Soln #',
                                       'tc_soln': 'TC Soln #',
                                       'crack_sizes': 'Crack Sizes',
                                       }

        self.gen_crack_combo_list = ['K Values', 'Betas', 'Nasgro']

        self.gen_crack_checkbutton_options = {'K_ave': 'K Average',
                                              'K_c': 'K Length',
                                              'K_a': 'K Depth'}

        self.program_text_options = {'windows_dir': 'text',
                                     'unix_dir': 'Unix Directory:',
                                     'unix_username': 'Unix Username',
                                     'unix_password': 'Unix Password:',
                                     'base_file_name': 'Base file name:',
                                     'spec_file_name': 'Spec file/DB Dir:'}

        self.program_checkbutton_options = {'gen_input': 'Generate input file',
                                            'mod_input': 'Modify initial flaw size(s)',
                                            'gen_ksh': 'Generate JCL (ksh) file',
                                            'run_rassp': 'Run RASSP',
                                            'process_output': 'Process output'}

        self.input_file_text_options = {'flaw_sizes_a': 'Initial Flaw Sizes(a)',
                                        'flaw_sizes_c': 'Initial Flaw Sizes(c)',
                                        'a1': 'Crack Growth Limit(a)',
                                        'c1': 'Crack Growth Limit(c)',
                                        'net': 'Net Ratio',
                                        'dls': 'DLS',
                                        }

        self.input_file_checkbutton_options = {'a=c': 'a=c'}

        self.input_file_radiobutton_options = {
                                    'spec_type': {'card_n': 'CARDN Spectrum (Fleet)',
                                                  'card_s': 'CARDS Spectrum (FSFT)'}
                                    }

        self.set_filter_combobox_vals()
        self.set_mat_listbox_vals()

        # Set the current material selection to the fist in the list
        self.selected_material = self.material_list.get_current_list()[0]

    # =============================================================================
    #   TODO Method to read in all of the data fields from a text file  (Crack case, geometry, stress inputs etc.)
    #   Havning the info in a text file will make the process cleaner and easier to add infomraiton
    # =============================================================================
    def read_input_field_file(self):

        current_section = 'null'
        input_file = open(
            '//Sw.nos.boeing.com/b1bdata/data300$/groups/structures_3/users_data/Wooten/00_Tools/RASSP_Automation'
            '/Util/data_input.txt', 'r')

    # =============================================================================
    #   Sets up all of the connections between this controller and a material view instance
    # =============================================================================
    def bind_mat_view(self, view):

        # Bind the material view to this instance of the controller
        self.mat_view = view

        # Creates the material view by passing in the data needed for the material filter comboboxes and the current
        # material listbox
        self.mat_view.create_view(self.mat_filter_combobox_lists, self.mat_listbox_strings)

        # Place the material view in the root frame at grid location 0,0
        self.mat_view.grid(row=0, column=0)

        self.mat_view.listboxes['current_mat_list'].select_set(0)

        # Bind the list_box_selected method to the ListboxSelect event
        # Will be called when the user selects a material from the material listbox
        self.mat_view.listboxes['current_mat_list'].bind("<<ListboxSelect>>", self.listbox_selected)

        # Bind all of the comboboxes to the combo_box_selected method
        # Will be called when the user makes a selection in any of the comboboxes
        for mat_filter in self.mat_filters:
            self.mat_view.comboboxes[mat_filter].bind('<<ComboboxSelected>>', self.mat_combobox_selected)

        # Bind the reset filters button to the reset_button_pressed method
        self.mat_view.buttons['Reset Filters'].configure(command=self.reset_button_pressed)

    # =============================================================================
    #   Sets up all of the connections between this controller and the input view instance
    # =============================================================================
    def bind_input_view(self, view):

        # Bind the input view to this instance of the controller
        self.input_view = view

        # Create the input view by passing in the needed parameters for the view
        # This includes the nested dictionary of crack cases
        self.input_view.create_view(self.crack_cases, self.crack_cases_titles,
                                    self.gen_crack_text_options, self.gen_crack_combo_list,
                                    self.gen_crack_checkbutton_options,
                                    self.program_text_options, self.program_checkbutton_options,
                                    self.input_file_text_options, self.input_file_checkbutton_options,
                                    self.input_file_radiobutton_options)

        # Bind the crack case combobox selection to the crack_case_combobox_selected method
        self.input_view.comboboxes['crack_case'].bind('<<ComboboxSelected>>', self.crack_case_combobox_selected)

        # Bind the gen crack option combobox selection to the gen_crack_option_selected method
        self.input_view.comboboxes['gen_crack_options'].bind('<<ComboboxSelected>>', self.gen_crack_option_selected)

        self.input_view.bind_all('<Any-KeyPress>', self.key_pressed)

        # Bind the windows dir button to the windows_dir_button_pressed method
        self.input_view.buttons['windows_dir'].configure(command=self.windows_dir_button_pressed)

        self.input_view.buttons['run_rassp'].configure(command=self.run_rassp_button_pressed)
        
        self.input_view.checkbuttons['a=c'].configure(command=self.checkbutton_state_changed)

        self.crack_case_selected = '1010'

        self.set_initial_vars()

    def set_initial_vars(self):
        if os.path.isfile(self.rassp_install_location + 'Temp/input_vars.txt'):
            vars_temp_file = open(self.rassp_install_location + 'Temp/input_vars.txt', 'r')

            lines = vars_temp_file.readlines()
            for line in lines:
                line_split_list = line.split('?')
                variable = line_split_list[0]
                value = line_split_list[1].strip()

                if variable in self.input_view.combobox_StringVars:
                    self.input_view.set_combobox_StringVar(variable, value)

                elif variable in self.mat_view.combobox_StringVars:
                    self.mat_view.set_combobox_StringVar(variable, value)

                elif variable in self.input_view.text_fields:
                    value = line_split_list[1].replace(' ', '\n')
                    self.input_view.set_text_field_value(variable, value)

                # Cant strip spaces before the first input view text fields check
                # Check and see if the variable is NOT an IntVar, then it must be a StringVar
                elif variable not in self.input_file_checkbutton_options and variable not in self.program_checkbutton_options:
                    # if variable in self.input_view.entry_StringVars:
                    if variable == 'Kc':
                        self.mat_view.set_entry_StringVar(variable, value)
                    else:
                        self.input_view.set_entry_StringVar(variable, value)

                # If it is an IntVar
                else:
                    self.input_view.set_entry_IntVar(variable, int(value))
            self.mat_combobox_selected()
            self.crack_case_combobox_selected()
            self.checkbutton_state_changed()
            vars_temp_file.close()

    # =============================================================================
    #   Method to create a dictionary of values to populate the comboboxes used for material filters
    #   The keys of the dict are the mat_filters - the material instance variables that
    #   the material list shown to the user will be filtered on
    #   The value corresponding to each key is the list of available parameters to sort the key off of
    #   ie. The value for the key 'temper' will a list containing every unique temper of the
    #   materials in the current material list
    # =============================================================================
    def set_filter_combobox_vals(self):

        # Step though each one of the material filters from the mat_filters list
        # These are named the same as the material instance variables that we will filter on'
        # Which is fairly important...
        for mat_filter in self.mat_filters:

            # Will need a combobox showing the available values to filter the materials list with
            # Creates a list of the unique values of the current variable in the material list
            current_combobox_list = []

            # Step through the current material list as material
            for material in self.material_list.get_current_list():
                # Append the current material instance variable corresponding to the material filter value
                current_combobox_list.append(str(vars(material)[mat_filter]))
            # current_combobox_list.sort()    - maybe, come back to this
            # Set the current combobox values list to the unique set of material variables for this filter value
            self.mat_filter_combobox_lists[mat_filter] = list(set(current_combobox_list))
            self.mat_filter_combobox_lists[mat_filter].sort()
            self.mat_filter_combobox_lists[mat_filter].insert(0, self.filter_title_map[mat_filter])

    # =============================================================================
    #   Method to create a list of strings that will be displayed to the user in the
    #   material listbox for their selection
    #   The method steps through the current material list and constructs a string representation
    #   of each material - contains a number of parameters for the string but not all
    #   It then appends each material string to the instance variable mat_listbox_strings
    # =============================================================================
    def set_mat_listbox_vals(self):
        self.mat_listbox_strings = []

        for material in self.material_list.get_current_list():
            material_string = (str(vars(material)['mat_name']).ljust(13) + str(vars(material)['prod_form']).rjust(13) +
                               str(vars(material)['temper']).rjust(14) +
                               str(vars(material)['environment']).rjust(18) + str(vars(material)['orientation']).rjust(
                        4) +
                               str(vars(material)['procure_spec']).rjust(15) + (
                                       'Fty=' + str(vars(material)['Fty'])).rjust(12))

            self.mat_listbox_strings.append(material_string)

    def set_filter_combobox_view(self):
        self.set_filter_combobox_vals()
        for combobox_name in self.mat_view.comboboxes:
            self.mat_view.comboboxes[combobox_name]['values'] = self.mat_filter_combobox_lists[combobox_name]

    def set_mat_listbox_view(self):
        self.set_mat_listbox_vals()
        self.mat_view.listboxes['current_mat_list'].delete(0, 'end')

        for material in self.mat_listbox_strings:
            self.mat_view.listboxes['current_mat_list'].insert('end', material)

    def equate_a_c(self):
        self.input_view.set_entry_StringVar('c1', self.input_view.get_entry_StringVar('a1'))
        self.input_view.set_entry_StringVar('flaw_sizes_c', self.input_view.get_entry_StringVar('flaw_sizes_a'))

    # ============================================================================================================
    #     *******All of the callback / binded methods are below*******
    # ============================================================================================================

    # Called when a selection is made in the list box which contains the filered materials list
    def listbox_selected(self, event=None):
        selection = self.mat_view.get_listbox_selection('current_mat_list')
        if selection:
            index = selection[0]

            self.selected_material = self.material_list.get_current_list()[index]

            # TODO Update the current Kc plot picture

    # =============================================================================
    #     Called when a selection is made in any of the material filter comboboxes
    #     Loops through all of the material filter comboboxes and filters the master mateial
    #     list from them. The view will then be updated to show only the remaining materials
    #     and available material filter options.
    #
    #     The current material list is reset at the beginning of each call to this method,
    #     so that each time a combobox selection is made, the materials are filtered on only
    #     the current values.
    #     ie. If the User filters on orientation and then wants to reset the orientation filter,
    #     they can just set the filter back to its title option of 'Orientation'
    # =============================================================================
    def mat_combobox_selected(self, event=None):

        # Reset the material list to the full master list
        # This is to ensure that the list is only sorted on the current material filter values
        self.material_list.reset()

        # What we will actually sort the materials list on
        # The comboboxes where the first value is selected(the title) wont be used to sort
        filter_dict = {}

        # Loop through all of the material filter comboboxes (dictionary) from the material view
        # The combobox  will also share the same name as the corresponding 
        # material instance variable. 
        # This makes sorting the material list based on a dictionary easier to handle
        for filter_combo_box_id in self.mat_view.comboboxes:

            # Set the current_filter seleciton to the current value of the corresponding filter combobox
            # current_filter_selection = self.mat_view.comboboxes[filter_combo_box_id].get()
            current_filter_selection = self.mat_view.get_combobox_StringVar(filter_combo_box_id)

            # If the current filter combobox selection value is not the title,
            # Add it to the dictionary of values that will be used to sort the material list
            if current_filter_selection not in self.mat_filter_titles:
                filter_dict[filter_combo_box_id] = current_filter_selection

        # Filters the instance material list
        # Filtered list is accessible from the get_current_list() method of the materials list instance
        self.material_list.filter_materials(filter_dict)

        # updates the views
        self.set_filter_combobox_view()
        self.set_mat_listbox_view()

        # TODO add update Kc plot functionality

    def crack_case_combobox_selected(self, event=None):
        crack_code = self.input_view.get_combobox_StringVar('crack_case').split()[0]
        self.crack_case_selected = crack_code
        self.input_view.frames['crack_case_input'].destroy()
        self.input_view.create_crack_case_input_frame(self.input_view.label_frames['crack_case'],
                                                      'crack_case_input', crack_code)

        if self.crack_case_selected == '1080' or self.crack_case_selected == '2080':
            self.input_view.activate_combobox('gen_crack_options')
            gen_crack_option = self.input_view.get_combobox_StringVar('gen_crack_options')
            self.input_view.grid_replace_frame(gen_crack_option)
        else:
            self.input_view.deactivate_combobox('gen_crack_options')
            self.input_view.remove_gen_crack_frames()

    def gen_crack_option_selected(self, event=None):
        self.input_view.remove_gen_crack_frames()
        gen_crack_option = self.input_view.get_combobox_StringVar('gen_crack_options')
        self.input_view.grid_replace_frame(gen_crack_option)

        self.gen_crack_selected = gen_crack_option

    def checkbutton_state_changed(self):
        state_ac = self.input_view.get_ac_state()

        if state_ac == 1:
            self.equate_a_c()
            self.input_view.disable_entry('c1')
            self.input_view.disable_entry('flaw_sizes_c')
        if state_ac == 0:
            self.input_view.enable_entry('c1')
            self.input_view.enable_entry('flaw_sizes_c')

    def reset_button_pressed(self):
        self.material_list.reset()
        for combobox_name in self.mat_view.comboboxes:
            self.mat_view.comboboxes[combobox_name].current(0)

        self.set_filter_combobox_view()
        self.set_mat_listbox_view()

    def windows_dir_button_pressed(self):
        self.windows_dir = self.input_view.get_windows_dir()

    def key_pressed(self, event):
        if self.input_view.get_ac_state() == 1:
            self.equate_a_c()

    # =============================================================================
    #     This method will grab all of the inputs the user has given and execute the rassp program.
    # =============================================================================
    def run_rassp_button_pressed(self):

        # In case the key_pressed method was not called (user just hit run)
        if self.input_view.get_ac_state() == 1:
            self.equate_a_c()

        # Method to write all of the inputs to a temp file that can
        # be read in when the program runs again
        self.set_temp_vars()

        # This is just to make accessing these variables easier
        text_inputs = self.text_input_values.copy()

        # Also just grabbing these variables now to make accessing them below more concise
        flaw_sizes_a = self.input_view.get_entry_StringVar('flaw_sizes_a').split()
        flaw_sizes_a.sort()
        a_1 = self.input_view.get_entry_StringVar('a1')
        flaw_sizes_c = self.input_view.get_entry_StringVar('flaw_sizes_c').split()
        flaw_sizes_c.sort()
        c_1 = self.input_view.get_entry_StringVar('c1')

        ksh_file_name = f"{self.text_input_values['base_file_name']}.ksh"

        # Create the RASSP object
        self.rassp = RASSP.RASSP(text_inputs['unix_username'], text_inputs['unix_password'],
                                 text_inputs['unix_dir'], text_inputs['windows_dir'],
                                 text_inputs['base_file_name'], text_inputs['spec_file_name'],
                                 ksh_file_name)

        # =============================================================================
        #         The next section will go through all of the checkbutton inputs to
        #         See which aspects of the program to run
        # =============================================================================
        # If the user selected the generate input checkbox we will have to build the full input file
        if self.checkbox_input_values['gen_input'] == 1:

            # Will update the current selected material
            self.listbox_selected()

            # Reset some variables in case they are still active
            # Would be a problem if the user pressed run twice without closing
            self.gen_crack_list = []
            self.crack_case = None

            # Set the material Kc value to the current value of the Kc entry
            Kc = self.mat_view.get_entry_StringVar('Kc')
            self.selected_material.set_Kc(Kc)

            # Get the design limit stress from the input
            dls = self.input_view.get_entry_StringVar('dls')
            # If the field was left blank, set it to the default value of 2.0
            if dls == '':
                dls = '2.0'

            net = self.input_view.get_entry_StringVar('net')
            # If the field was left blank, set to the default value of 1.0
            if net == '':
                net = '1.0'

            # Method to set all the paramaters of the crack case class
            # Needed to define the input file
            self.set_crack_case()

            # Indicates a CARDN Spectrum - need STF and to modify $START parameter in input file
            if self.radiobutton_input_values['spec_type'] == 0:
                start = 'COMPILE,SOLUTION=CRKGRO,FILE9=100,REPORT,NPRINTF'
                spectrum = 'CARDN=11,RANGE,'
                stf_temp = self.input_view.get_text_field_value('stf')
                stf_temp = stf_temp.replace(" ", "")
                stf = ''
                lines = stf_temp.split("\n")
                for line in lines:
                    if 'V=' in line and 'K=' in line and 'E=' in line:
                        append_string = ' ' + line + '\n'
                    else:
                        append_string = '       ' + line + '\n'
                    stf = stf + append_string
                stf = stf.rstrip()

            # If CARDS Spectrum, $Start parameter changes
            elif self.radiobutton_input_values['spec_type'] == 1:
                start = 'SPECTRUM,SOLUTION=CRKGRO,FILE9=100,REPORT,NPRINTF'
                spectrum = 'CARDS=11,RANGE,'
                stf = ""
            two_D = False
            if self.input_view.get_ac_state() != 1:
                two_D = True

                # Check if the crack case is a standard one or a 1080/2080 - need to grab the beta values
            if self.crack_case_selected == '1080' or self.crack_case_selected == '2080':

                # Makes sure that the right general crack option is read from the input
                self.gen_crack_option_selected()

                # Extract the needed nasgro parameters from the dict of entry strings
                geom_params = ['t', 'W', 'D', 'B']
                geometry = {}
                for param in geom_params:
                    value = self.input_view.get_entry_StringVar(param)
                    geometry[param] = value
                far_field = self.input_view.get_entry_StringVar('far_field')

                kind = 'EDGE CRACK'

                k_choice = 'K_ave'
                if self.checkbox_input_values['K_ave'] == 1:
                    k_choice = 'K_ave'

                elif self.checkbox_input_values['K_c'] == 1:
                    k_choice = 'K_c'

                elif self.checkbox_input_values['K_a'] == 1:
                    k_choice = 'K_a'

                # Check which kind of general crack case it is
                if self.gen_crack_selected == 'Nasgro':

                    mat_props = vars(self.selected_material)

                    stress_params = ['S0', 'S1', 'S2', 'S3', 'S4']
                    stresses = {}
                    for param in stress_params:
                        value = self.input_view.get_entry_StringVar(param)
                        if value == '':
                            value = '0.0'
                        stresses[param] = value

                    # Some random parameters needed to build the batch file
                    config_name_cc = "CC"
                    config_name_tc = "TC"

                    # Pull the user specified CC & TC solution #'s
                    # Currently only works for CC16, TC03 & TC05
                    cc_num = int(self.input_view.get_entry_StringVar('cc_soln'))
                    tc_num = int(self.input_view.get_entry_StringVar('tc_soln'))

                    crack_code_cc = {'type': 'CC', 'number': cc_num}
                    crack_code_tc = {'type': 'TC', 'number': tc_num}

                    # Cracked ligament solution
                    # crack_code_cc = {'type': 'CC', 'number': 15}
                    # crack_code_tc = {'type': 'TC', 'number': 19}                    

                    # Need to loop through the crack sizes to separate the CC and TC cases
                    crack_sizes = self.input_view.get_text_field_value('crack_sizes').split()
                    # Sort the values so the loop works correctly
                    crack_sizes.sort()

                    crack_sizes_cc_c = []
                    crack_sizes_cc_a = []
                    crack_sizes_tc = []

                    if (two_D == False):

                        # Loop through all crack sizes and split them up accordingly
                        for crack_size in crack_sizes:
                            if float(crack_size) < float(geometry['t']):
                                crack_sizes_cc_c.append(crack_size)
                                crack_sizes_cc_a.append(crack_size)

                            elif float(crack_size) > float(geometry['t']):
                                crack_sizes_tc.append(crack_size)

                        gen_crack_cc = Gen_Crack.Gen_Crack()
                        gen_crack_cc.run_nassif(kind, config_name_cc, crack_code_cc, geometry, stresses, mat_props,
                                                crack_sizes_cc_a, crack_sizes_cc_c, k_choice)

                        gen_crack_cc.calc_betas(far_field, geometry, self.crack_case_selected)
                        self.gen_crack_list.append(gen_crack_cc)

                        # Thru crack values, there will only be one set of these even if it is 2 Dimentional analysis
                        gen_crack_tc = Gen_Crack.Gen_Crack()
                        gen_crack_tc.run_nassif(kind, config_name_tc, crack_code_tc, geometry, stresses, mat_props,
                                                crack_sizes_tc, crack_sizes_tc, k_choice)
                        gen_crack_tc.calc_betas(far_field, geometry, self.crack_case_selected)
                        self.gen_crack_list.append(gen_crack_tc)

                    # If 2D growth is activated, the program will calculate K_a and K_c at each crack length,
                    # The program will then calculate a new crack depth value (a) for a corresponding length (c)
                    # using the Paris rule...
                    # Once the depth dimenion (a) is greater than thicknes, the program will switch to thru thickness cracks
                    # for the remaining length (c) values
                    else:

                        # 2D crack case will requiire 3 sets of input files and Beta calculations
                        # Crack growth in the depth direction using Ka
                        # Corner Crack growth in the length direction using Kc
                        # Thru crack growth in the length direction using Kc

                        # Will need a Beta gradient & input file for each initial flaw size
                        for initial_flaw in flaw_sizes_a:

                            # Material parameter needed for Paris law calculation
                            Nu = vars(self.selected_material)['Nu']

                            a_0 = initial_flaw
                            c_0 = initial_flaw

                            a_1 = a_0
                            c_1 = c_0

                            # Couter to see how many flaw sizes we actually make it through
                            # Will skip any flaw sizes less than the current initial flaw size (only for 2D)
                            j = 0
                            # Loop through all of the input crack lengths
                            for i in range(len(crack_sizes)):

                                # If the current crack size is less than the initial flaw for this iteration, skip it
                                if crack_sizes[i] < initial_flaw:
                                    continue

                                # If the depth value is still below the thickness, continue with the calculation
                                # Else switch to thru crack solution
                                if float(a_1) < float(geometry['t']):

                                    # Create a new corner crack object
                                    gen_crack_cc = Gen_Crack.Gen_Crack()

                                    # run nassif program
                                    # Input is a list of a and c values, although it will only contain one value each
                                    gen_crack_cc.run_nassif(kind, config_name_cc, crack_code_cc, geometry, stresses,
                                                            mat_props, [a_1], [c_1], k_choice)

                                    # Calculate the beta values for this iteration
                                    gen_crack_cc.calc_betas(far_field, geometry, self.crack_case_selected)

                                    # Add this iteration to the class varabile general crack case list
                                    self.gen_crack_list.append(gen_crack_cc)

                                    # If one iteration has already been completed, we can now calculate the next
                                    # crack depth size using Paris rule and the Ka / Kc values from the last run
                                    previous_iteration = self.gen_crack_list[j]

                                    c_1 = float(crack_sizes[i + 1])

                                    a_1 = str(previous_iteration.calc_a_1(float(a_0), float(c_0), c_1, Nu))
                                    a_0 = a_1
                                    c_0 = c_1
                                    if (a_1 == 'None'):
                                        a_1 = geometry['t']


                                else:
                                    crack_sizes_tc.append(crack_sizes[i])

                                j = j + 1

                            # Create the TC object to run the remainder of the crack sizes that are thru thickness
                            gen_crack_tc = Gen_Crack.Gen_Crack()
                            gen_crack_tc.run_nassif(kind, config_name_tc, crack_code_tc, geometry, stresses, mat_props,
                                                    crack_sizes_tc, crack_sizes_tc, k_choice)
                            gen_crack_tc.calc_betas(far_field, geometry, self.crack_case_selected)
                            self.gen_crack_list.append(gen_crack_tc)

                            initial_flaw_str = str(initial_flaw).replace('.', '')
                            iteration_file_name = text_inputs['base_file_name'] + '_' + initial_flaw_str

                            Gen_Crack.Gen_Crack.write_to_file(text_inputs['windows_dir'], iteration_file_name,
                                                              self.gen_crack_list)

                            # Three input files must be created
                            # Crack growth in the depth direction using Ka
                            # Corner Crack growth in the length direction using Kc
                            # Thru crack growth in the length direction using Kc
                            crack_depths = []
                            crack_lengths = []
                            k_depth = []
                            k_length = []

                            for gen_crack in self.gen_crack_list:
                                for i in range(len(gen_crack.crack_sizes_a)):

                                    if gen_crack.crack_code['type'] == "CC":
                                        crack_depths.append(gen_crack.crack_sizes_a[i])
                                        k_depth.append(str(float(gen_crack.k_vals_array[0][1]) * 1000))

                                    crack_lengths.append(gen_crack.crack_sizes_c[i])
                                    k_length.append(str(float(gen_crack.k_vals_array[i][2]) * 1000))

                            input_iterations = ['_0_Depth', '_1_1080', '_2_2080']
                            iteration_sizes = [crack_depths, crack_lengths, crack_lengths]
                            iteration_k_vals = [k_depth, k_length, k_length]

                            for i in range(len(input_iterations)):
                                self.gen_crack_list = []

                                input_iteration_name = input_iterations[i]
                                crack_sizes = iteration_sizes[i]
                                k_vals = iteration_k_vals[i]

                                gen_crack = Gen_Crack.Gen_Crack()
                                gen_crack.set_k_vals(crack_sizes, k_vals)
                                gen_crack.calc_betas(far_field, geometry, self.crack_case_selected)

                                self.gen_crack_list.append(gen_crack)

                                input_file = Input_File.Input_File(self.selected_material, self.crack_case,
                                                                   self.gen_crack_list, net=net, dls=dls,
                                                                   start=start, spectrum=spectrum, stf=stf)
                                input_file_name = iteration_file_name + input_iteration_name + '.input'
                                input_file.create_input_file(input_file_name, location=text_inputs['windows_dir'])

                                input_file = None


                elif self.gen_crack_selected == 'K Values':
                    crack_sizes = self.input_view.get_text_field_value('crack_sizes_k').split()
                    k_vals = self.input_view.get_text_field_value('K Values').split()

                    # Create the gen_crack object, insert K values, and calc betas
                    gen_crack = Gen_Crack.Gen_Crack()
                    gen_crack.set_k_vals(crack_sizes, k_vals)
                    gen_crack.calc_betas(far_field, geometry, self.crack_case_selected)

                    self.gen_crack_list.append(gen_crack)

                    Gen_Crack.Gen_Crack.write_to_file(text_inputs['windows_dir'], text_inputs['base_file_name'],
                                                      self.gen_crack_list)
                elif self.gen_crack_selected == 'Betas':
                    crack_sizes = self.input_view.get_text_field_value('crack_sizes_beta').split()
                    betas = self.input_view.get_text_field_value('Betas').split()

                    # create the gen_crack object, insert betas
                    gen_crack = Gen_Crack.Gen_Crack()
                    gen_crack.set_betas(crack_sizes, betas)

                    self.gen_crack_list.append(gen_crack)

            if two_D == False:
                Gen_Crack.Gen_Crack.write_to_file(text_inputs['windows_dir'], text_inputs['base_file_name'],
                                                  self.gen_crack_list)

                input_file = Input_File.Input_File(self.selected_material, self.crack_case, self.gen_crack_list,
                                                   net=net, dls=dls, start=start, spectrum=spectrum, stf=stf)
                input_file_name = text_inputs['base_file_name'] + '.input'
                input_file.create_input_file(input_file_name, location=text_inputs['windows_dir'])

                # If input file is to be created, also modify it
                Input_File.Input_File.mod_input_crack_size(text_inputs['base_file_name'], flaw_sizes_a, flaw_sizes_c,
                                                           location=text_inputs['windows_dir'], remove_base=True,
                                                           limit_a=a_1, limit_c=c_1)

        if self.checkbox_input_values['mod_input'] == 1:
            Input_File.Input_File.mod_input_crack_size(text_inputs['base_file_name'], flaw_sizes_a, flaw_sizes_c,
                                                       location=text_inputs['windows_dir'], remove_base=True,
                                                       limit_a=a_1, limit_c=c_1)
        if self.checkbox_input_values['gen_ksh'] == 1:

            if self.radiobutton_input_values['spec_type'] == 0:
                self.rassp.create_ksh(ksh_file_name, 'CARDN', text_inputs['spec_file_name'])
            else:
                self.rassp.create_ksh(ksh_file_name, 'CARDS', text_inputs['spec_file_name'])

        if self.checkbox_input_values['run_rassp'] == 1:
            self.rassp.rassp_execute(5)

        if self.checkbox_input_values['process_output'] == 1:
            output = Process_Output.Process_Output(self.rassp, flaw_sizes_a)
            output.plot_results()
            output.plot_results_excel(text_inputs['base_file_name'])

    def set_crack_case(self):
        # This is the dictionary that all of the crack case parameters will be added to
        crack_case_args = {}

        # First get the geometry inputs from the crack_case view.
        # Only the variables corresponding to the selected crack case will be recorded during the loop
        # This will leave all other entries blank within RASSP which isn't really needed - but is good practice
        for variable_name in self.input_view.entry_StringVars:

            value = self.input_view.get_entry_StringVar(variable_name)

            # If the variable is one of the geometry values needed for this crack_case
            if variable_name in self.crack_cases[self.crack_case_selected]:

                # If the current variable is edge distance, convert to eccentricity for RASSP
                if variable_name == 'B':
                    w = float(self.input_view.get_entry_StringVar('W'))
                    b = float(value)
                    e = (w / 2) - (b)

                    if e / 10 > 1:
                        e = str(round(e, 2))
                    else:
                        e = str(round(e, 3))
                    crack_case_args['e'] = e

                # If the current variable is the diameter, change to radius for RASSP
                elif variable_name == 'D':
                    r = round(float(value) / 2, 3)
                    crack_case_args['r'] = r
                else:
                    crack_case_args[variable_name.lower()] = value

        # Extract the material properties needed for the crack case class
        # Make a list of the paramaters needed, then loop through all mat props
        # and add the needed variables to the crack_case_args dict
        crack_case_mat_props = ['Rp', 'Rm', 'Rso']
        for mat_prop in vars(self.selected_material):
            if mat_prop in crack_case_mat_props:
                crack_case_args[mat_prop] = vars(self.selected_material)[mat_prop]

        dls = self.input_view.get_entry_StringVar('dls')
        # If the dls variable was set by the user, include it in the crack_case_args
        # If it wasn't, the dls will default to 10
        if dls != '':
            crack_case_args['dls'] = dls

        # Set the code argument for the crack_case class
        crack_case_args['code'] = self.crack_case_selected

        # I hate how the code below is repeated, but it isn't worth the trouble to redo it
        # Sets the crack growth starting values and limits for both directions
        flaw_sizes_a = self.input_view.get_entry_StringVar('flaw_sizes_a').split()
        flaw_sizes_a.sort()
        a_1 = self.input_view.get_entry_StringVar('a1')

        flaw_sizes_c = self.input_view.get_entry_StringVar('flaw_sizes_c').split()
        flaw_sizes_c.sort()
        c_1 = self.input_view.get_entry_StringVar('c1')

        crack_case_args['a_init'] = flaw_sizes_a[0]
        crack_case_args['c_init'] = flaw_sizes_c[0]
        crack_case_args['a_fin'] = a_1
        crack_case_args['c_fin'] = c_1

        self.crack_case = Crack_Case.Crack_Case(**crack_case_args)

    def set_gen_crack_list(self):

        pass

    def set_temp_vars(self):

        if not os.path.isdir(self.rassp_install_location + "Temp/"):
            os.mkdir(self.rassp_install_location + "Temp/")

        vars_temp_file = open(self.rassp_install_location + 'Temp/input_vars.txt', 'w')

        # Loop through the input view StringVar variables (text inputs) and add them to the text_input_values dict
        for text_entry_name in self.input_view.entry_StringVars:
            text_entry_value = self.input_view.entry_StringVars[text_entry_name].get()
            self.text_input_values[text_entry_name] = text_entry_value

            vars_temp_file.write(text_entry_name + '?' + text_entry_value + '\n')

        # Do the same for the material view object, currently only matters for Kc parameter
        for text_entry_name in self.mat_view.entry_StringVars:
            text_entry_value = self.mat_view.entry_StringVars[text_entry_name].get()
            self.text_input_values[text_entry_name] = text_entry_value

            vars_temp_file.write(text_entry_name + '?' + text_entry_value + '\n')

        # Loop through all of the input view IntVar variables (checkbutton inputs) and add them to the
        # checkutton_input_values dict
        for checkbutton_name in self.input_view.checkbutton_IntVars:
            checkbutton_value = self.input_view.checkbutton_IntVars[checkbutton_name].get()
            self.checkbox_input_values[checkbutton_name] = checkbutton_value

            vars_temp_file.write(checkbutton_name + '?' + str(checkbutton_value) + '\n')

        for radiobutton_name in self.input_view.radiobutton_IntVars:
            radiobutton_value = self.input_view.radiobutton_IntVars[radiobutton_name].get()
            self.radiobutton_input_values[radiobutton_name] = radiobutton_value

        # Loop through all of the text_fields (multiline strings) and store them as well
        # Going to convert to a single line string to store in the temp file
        # Will make it cleaner to read through and if we don't it could cause issues
        for text_field in self.input_view.text_fields:
            text_field_value = self.input_view.get_text_field_value(text_field).replace(' ', '')
            text_field_value = text_field_value.replace('\n', ' ')
            vars_temp_file.write(text_field + '?' + text_field_value + '\n')

        for combobox_name in self.mat_view.comboboxes:
            combobox_value = self.mat_view.get_combobox_StringVar(combobox_name)
            self.combobox_input_values[combobox_name] = combobox_value

            vars_temp_file.write(combobox_name + '?' + combobox_value + '\n')

        for combobox_name in self.input_view.comboboxes:
            combobox_value = self.input_view.get_combobox_StringVar(combobox_name)
            self.combobox_input_values[combobox_name] = combobox_value

            vars_temp_file.write(combobox_name + '?' + combobox_value + '\n')

        vars_temp_file.close()
