# -*- coding: utf-8 -*-
"""


@author: ry219e
"""

import tkinter.filedialog
import tkinter as tk
from tkinter import ttk
from abc import abstractmethod, ABC


# =============================================================================
# The abstact View class that is a child of the tk.Frame class
# Abstracted to ensure a create_view() method is implemented in all instances
# create_view acts almost as a way to create all of the view elements after the 
# view has already been initialized. Needs to be initialized first so it can 
# be bound to the correct controller
# =============================================================================
class View(ABC, tk.Frame):

    def __init__(self, master):

        self.master = master

        # Each instance of the view class will have a dictionary for each kind of element it may have
        self.buttons = {}
        self.labels = {}

        self.entries = {}
        self.entry_StringVars = {}

        self.entry_fields = {}

        self.text_fields = {}
        self.text_boxes = {}

        self.comboboxes = {}
        self.combobox_StringVars = {}

        self.listboxes = {}

        self.label_frames = {}
        self.checkbuttons = {}
        self.checkbutton_IntVars = {}

        self.radiobuttons = {}
        self.radiobutton_IntVars = {}

        self.plots = {}
        self.image = {}
        super().__init__()

    @abstractmethod
    def create_view():
        raise NotImplementedError

    def create_label_frame(self, master, name, title, row, column, sticky='w', padx=5, pady=0):
        self.label_frames[name] = tk.LabelFrame(self, text=title, bd=0, font=('consolas', '11', 'bold'))
        self.label_frames[name].grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)
        self.label_frames[name].grid_rowconfigure(0, weight=1)
        self.label_frames[name].grid_columnconfigure(0, weight=1)

    def create_combobox(self, master, name, combo_list, row, column, span=1, padx=0, pady=0, width=17, height=7):

        if name not in self.combobox_StringVars:
            self.combobox_StringVars[name] = tk.StringVar()

        self.comboboxes[name] = ttk.Combobox(master, values=combo_list, state='readonly', width=width, height=height)
        self.comboboxes[name].configure(textvariable=self.combobox_StringVars[name])
        self.comboboxes[name].current(0)
        self.comboboxes[name].grid(row=row, column=column, columnspan=span, sticky='w', padx=padx, pady=pady)

    # Generates an 'entry field' - just my name for a frame container for a label and text field together
    def create_entry_field(self, master, entry_name, prompt_text, row, column, padx=0, pady=1, sticky='w',
                           ljust=10, entry_width=7, columnspan=1, show=None):

        self.entry_fields[entry_name] = tk.Frame(master)
        self.entry_fields[entry_name].grid(row=row, column=column, columnspan=columnspan, sticky=sticky, padx=padx,
                                           pady=pady)

        # A tk.StingVar makes things easier, it will automatically update the entry text if the variable is changed
        # Also makes things easier if the entry needs to be greyed out
        if entry_name not in self.entry_StringVars:
            self.entry_StringVars[entry_name] = tk.StringVar()

        self.labels[entry_name] = tk.Label(self.entry_fields[entry_name], text=prompt_text.ljust(ljust),
                                           font=('consolas', '10'))
        self.entries[entry_name] = tk.Entry(self.entry_fields[entry_name],
                                            textvariable=self.entry_StringVars[entry_name],
                                            width=entry_width, font=('consolas', '10'), show=show)

        self.labels[entry_name].grid(row=0, column=0, sticky='nw')
        self.entries[entry_name].grid(row=0, column=1, sticky='ne')

    def create_text_field(self, master, text_field_name, prompt_text, row, column, padx=5, pady=1,
                          sticky='nw', text_width=13, text_height=15, rowspan=1):

        self.text_fields[text_field_name] = tk.Frame(master)
        self.text_fields[text_field_name].grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady,
                                               rowspan=rowspan)

        self.labels[text_field_name] = tk.Label(self.text_fields[text_field_name], text=prompt_text,
                                                font=('consolas', '10'))
        self.text_boxes[text_field_name] = tk.Text(self.text_fields[text_field_name],
                                                   height=text_height, width=text_width, font=('consolas', '10'))

        self.labels[text_field_name].grid(row=0, column=0, sticky='nw')
        self.text_boxes[text_field_name].grid(row=1, column=0, sticky='nw')

    def create_plot(self, master, name, filename, row, column, columnspan=2, sticky='e'):
        self.image[name] = tk.PhotoImage(file=filename)
        self.plots[name] = tk.Canvas(master, width=310, height=240)
        self.plots[name].create_image(155, 120, image=self.image[name])
        self.plots[name].grid(row=row, column=column, columnspan=3, sticky=sticky)

    def create_button(self, master, name, text, row, column, sticky='n', padx=0, pady=0):
        self.buttons[name] = tk.Button(master, font=('consolas', '10'))
        self.buttons[name]['text'] = text
        self.buttons[name].grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)

    def create_checkbutton(self, master, name, text, row, column, sticky='w'):
        self.checkbutton_IntVars[name] = tk.IntVar()
        self.checkbuttons[name] = tk.Checkbutton(master, text=text, variable=self.checkbutton_IntVars[name],
                                                 font=('consolas', '10'))
        # self.checkbuttons[name].select()
        self.checkbuttons[name].grid(row=row, column=column, sticky=sticky)

    def create_radiobutton(self, master, name, text, variable, value, row, column, sticky='w'):
        if variable not in self.radiobutton_IntVars:
            self.radiobutton_IntVars[variable] = tk.IntVar()

        self.radiobuttons[name] = tk.Radiobutton(master, text=text, variable=self.radiobutton_IntVars[variable],
                                                 value=value, font=('consolas', '10'))
        self.radiobuttons[name].grid(row=row, column=column, sticky=sticky)

    def create_listbox(self, master, name, mat_list, row, column, c_span=1, r_span=1, padx=0, pady=0):
        self.listboxes[name] = tk.Listbox(master, selectmode='SINGLE', height=10, width=95)
        self.listboxes[name].configure(font=('consolas', '10'))
        for material in mat_list:
            self.listboxes[name].insert('end', material)
        self.listboxes[name].grid(row=row, column=column, columnspan=c_span, rowspan=r_span,
                                  sticky='nw', padx=padx, pady=pady)

    def get_ac_state(self):
        return self.checkbutton_IntVars['a=c'].get()

    def get_windows_dir(self):
        windows_dir = tk.filedialog.askdirectory() + '/'
        self.entry_StringVars['windows_dir'].set(windows_dir)
        return windows_dir

    def get_listbox_selection(self, name):
        return self.listboxes[name].curselection()

    def get_combobox_StringVar(self, combobox_name):
        return self.combobox_StringVars[combobox_name].get()

    def get_entry_StringVar(self, entry_name):
        return self.entry_StringVars[entry_name].get()

    def get_text_field_value(self, name):
        return self.text_boxes[name].get("1.0", 'end-1c')

    def set_entry_StringVar(self, StringVar, value):
        if StringVar not in self.entry_StringVars:
            self.entry_StringVars[StringVar] = tk.StringVar()
        self.entry_StringVars[StringVar].set(value)

    def set_combobox_StringVar(self, StringVar, value):
        if StringVar not in self.combobox_StringVars:
            self.combobox_StringVars[StringVar] = tk.StringVar()
        self.combobox_StringVars[StringVar].set(value)

    def set_entry_IntVar(self, IntVar, value):
        if IntVar not in self.checkbutton_IntVars:
            self.checkbutton_IntVars[IntVar] = tk.IntVar()
        self.checkbutton_IntVars[IntVar].set(value)

    def set_text_field_value(self, text_field, value):
        if text_field not in self.text_fields:
            return
        self.text_boxes[text_field].delete(1.0, 'end')
        self.text_boxes[text_field].insert(1.0, value)

    def disable_entry(self, entry_name):
        self.entries[entry_name].configure(state=tk.DISABLED)

    def enable_entry(self, entry_name):
        self.entries[entry_name].configure(state=tk.NORMAL)

    def grid_remove_frame(self, name):
        self.frames[name].grid_remove()

    def grid_replace_frame(self, name):
        self.frames[name].grid()

    def deactivate_combobox(self, name):
        self.comboboxes[name].configure(state='disabled')

    def activate_combobox(self, name):
        self.comboboxes[name].configure(state='readonly')


class Material_View(View):
    def __init__(self, master=None):
        self.master = master
        super().__init__(master)  # Need to call the parent constructor - you just have to

        # Dict that will contain all of the comboboxes used to filter the material list
        self.filter_comboboxes = {}

        self.kc_plot = None  # Will be set in create_view

        """
        Dictionary that contains all of the lists needed to create the materiallist filter comboboxes 
        key - material paramater to filter the data on 
        value - list of unique material pramaters from the current material list
        """
        self.mat_filters_lists = {}

        """
        List containing the string representations of the current list 
        to show in the material liistbox
        """
        self.mat_string_list = []
        # Configure the location of the material view
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nsew', padx=10, pady=0)

    # =============================================================================
    #   Kinda like a constructor, builds all of the view elements
    #   Needs to be separate from the constructor so the view instance can be
    #   created and then binded to a controller, then the view can be built
    # =============================================================================
    def create_view(self, mat_filters_lists, mat_string_list):
        # set the variables needed for the comboboxes and listboxes to those
        # passed in from the controller
        self.mat_filters_lists = mat_filters_lists.copy()
        self.mat_string_list = mat_string_list.copy()

        # Create the container LabelFrame and place in the mat_view at 0,0 on the grid

        self.create_label_frame(self, 'mat_frame', 'Material', 0, 0, sticky='w', padx=0)

        self.kc_filename = "//Sw.nos.boeing.com/b1bdata/data300$/groups/structures_3/users_data/Wooten/Tools/RASSP_Automation/Util/Kc_1.gif"

        # The material variables that will be used to filter the material list
        mat_filters = ['mat_name', 'prod_form', 'temper', 'grade', 'procure_spec', 'orientation']

        # Create all of the material filter comboboxes
        index = 0

        # Loop through all of the material filters to create the comboboxes
        # mat_filter is the material variable that the combobox will contain a list of
        # ie. mat_filter = temper, the combobox will contain all unique tempers of the material list
        for mat_filter in mat_filters:
            # Create the combobox
            self.create_combobox(self.label_frames['mat_frame'], mat_filter, self.mat_filters_lists[mat_filter],
                                 row=0, column=index)
            index = index + 1

            # Create the reset filters button
        self.create_button(self.label_frames['mat_frame'], 'Reset Filters', 'Reset Filters', row=0, column=6)

        # Create the material list listbox
        self.create_listbox(self.label_frames['mat_frame'], 'current_mat_list', mat_string_list, row=1, column=0,
                            c_span=6, r_span=2, pady=10)

        # Create the kc plot picture
        # self.create_plot(self.label_frames['mat_frame'], 'Kc_plot', self.kc_filename, 1, 6 )

        # Create the input for label(? idk) for the KC entry
        # I ran out of grid spots so I had to contain this as one, but honestly it kinda works out better
        self.create_entry_field(self.label_frames['mat_frame'], 'Kc', 'Kc = ', 0, 7, padx=5, pady=1, sticky='nw',
                                ljust=5, entry_width=7)


class Input_View(View):
    def __init__(self, master=None):

        self.master = master

        super().__init__(master)  # Need to call the parent constructor - you just have to

        self.frames = {}  # Dict for all of the frames - usually just for layout purposes

        # Dict for all of the label frames
        # Crack case, input file options
        self.label_frames = {}

        # Nested dictionary of the crack codes and their needed parameters
        # Key - Crack Code
        # Value - Dict of crack code specific parameters
        # Key - variable name ie. W, t, D, B, t2, lt
        # Value - String representation of the variable ie. Width, Thickness, Hole Diameter
        self.crack_cases = {}

        # The crack case titles, this will be what the user sees in the combobox
        self.crack_cases_titles = {}

        self.program_checkbuttons = {}
        self.program_text_options = {}
        self.input_file_text_options = {}
        self.input_file_checkbuttons = {}
        self.input_file_radiobutton_names = []
        self.input_file_radiobuttons = {}
        self.nasgro_text_options = {}
        self.gen_crack_combo_list = []

        self.gen_crack_checkbuttons = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

    def create_view(self, crack_cases, crack_cases_titles,
                    nasgro_text_options, gen_crack_combo_list,gen_crack_checkbuttons,
                    program_text_options, program_checkbuttons,
                    input_file_text_options, input_file_checkbuttons, input_file_radiobuttons):

        # Make a copy of the crack cases dict and set it equal to the instance variable
        self.crack_cases = crack_cases.copy()

        # Make a copy of the crack case titles, this will be what the user sees in the combobox
        self.crack_cases_titles = crack_cases_titles.copy()

        self.nasgro_text_options = nasgro_text_options.copy()
        self.gen_crack_combo_list = gen_crack_combo_list.copy()
        self.gen_crack_checkbuttons = gen_crack_checkbuttons.copy()

        self.program_text_options = program_text_options.copy()
        self.program_checkbuttons = program_checkbuttons.copy()

        self.input_file_text_options = input_file_text_options.copy()
        self.input_file_checkbuttons = input_file_checkbuttons.copy()
        self.input_file_radiobuttons = input_file_radiobuttons.copy()

        # =============================================================================
        # Start with top level Label Frames: crack case, input file options, and program options
        # =============================================================================

        # Generate the frame that will house all of the crack case information
        self.create_label_frame(self, 'crack_case', 'Crack Case', 0, 0, sticky='nw', padx=0)

        # Generate the frame that will house all of the input file options
        self.create_label_frame(self, 'input_file_text_options', 'Input File Options', 0, 1, sticky='nw', padx=5)

        # Generate the frame that will house all of the RASSP input information
        self.create_label_frame(self, 'program_text_options', 'Program Options', 0, 2, sticky='ne', padx=0)

        # =============================================================================
        # Add all of the subelements into each label frame
        # =============================================================================
        # Creates the crack case combobox. Drop down select of all of the different crack cases
        self.create_combobox(self.label_frames['crack_case'], 'crack_case', self.get_crack_case_strings(), 0, 0,
                             width=31)

        # Create the crack case input frame. This is just to group all of the crack case parameters together
        self.create_crack_case_input_frame(self.label_frames['crack_case'], 'crack_case_input', '1010')

        self.create_combobox(self.label_frames['crack_case'], 'gen_crack_options', self.gen_crack_combo_list, 0, 1,
                             width=36)
        self.deactivate_combobox('gen_crack_options')

        self.create_gen_crack_frames(self.label_frames['crack_case'], 1, 1)

        self.create_input_file_options_fields(self.label_frames['input_file_text_options'], 'input_file_text_options')

        # Creates the program options input frame, where the user will specify which parts of the program to run
        # As well as specify file paths / unix username + password
        self.create_program_options_fields(self.label_frames['program_text_options'], 'program_text_options')

    # =============================================================================
    #   Generates the crack case input container frame
    #   Just a way to organize all of the crack case parameters together in a cleaner way.
    #   Also allows them to be updated easily by destroying the current frame and adding a new one
    # =============================================================================
    def create_crack_case_input_frame(self, master, name, crack_case, row=1, column=0, padx=0, pady=0, sticky='nw'):

        self.frames[name] = tk.Frame(master)  # create a frame and add it to the instance variable dict of frames

        # Create an index for the rows and columns so they can be changed while iterating throgh the
        # Crack case parameters in the dictionary
        row_index = 0
        column_index = 0

        # Iterate through all of the geometric terms for the given crack case and create an entry field for them
        for parameter in self.crack_cases[crack_case]:
            self.create_entry_field(self.frames[name], parameter, self.crack_cases[crack_case][parameter],
                                    row_index, column_index, ljust=20)
            row_index = row_index + 1

        # Place the frame in the grid
        self.frames[name].grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)

    def create_gen_crack_frames(self, master, row=1, column=1, padx=0, pady=0, sticky='w'):

        # create a frame and add it to the instance variable dict of frames
        for name in self.gen_crack_combo_list:
            self.frames[name] = tk.Frame(master)
            row_index = 0
            column_index = 0

            if name == 'Nasgro':
                width = 6
                for parameter in self.nasgro_text_options:
                    if parameter == 'crack_sizes':
                        continue
                    self.create_entry_field(self.frames[name], parameter, self.nasgro_text_options[parameter],
                                            row_index, column_index, ljust=12, entry_width=width, sticky='nw')
                    row_index = row_index + 1
                for parameter in self.gen_crack_checkbuttons:
                    self.create_checkbutton(self.frames[name], parameter, self.gen_crack_checkbuttons[parameter],
                                            row=row_index, column=column_index)
                    row_index = row_index + 1

                self.create_text_field(self.frames[name], 'crack_sizes', 'Crack size', 0, 1, sticky='nw', rowspan=100,
                                       text_width=12, text_height=15)

            elif name == 'K Values':
                self.create_entry_field(self.frames[name], 'far_field', self.nasgro_text_options['far_field'],
                                        row_index, 0, ljust=12, sticky='w', columnspan=2)
                self.create_text_field(self.frames[name], 'crack_sizes_k', 'Crack size', 1, 0, sticky='w')
                self.create_text_field(self.frames[name], name, name, 1, 1, sticky='w')
            else:
                self.create_text_field(self.frames[name], 'crack_sizes_beta', 'Crack size', 0, 0, sticky='w')
                self.create_text_field(self.frames[name], name, name, 0, 1, sticky='w')

            self.frames[name].grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
            self.grid_remove_frame(name)

    # =============================================================================
    #   Creates the options input container frame
    #   The options input frame contains all of the run options for the program.
    #   User will specify the windows and unix directories, unix password, and all of the run options:
    #   Create input file, create run file (ksh file), run RASSP, and process output
    # =============================================================================
    def create_program_options_fields(self, master, name, row=0, column=0, padx=0, pady=0, sticky='nw'):

        row_index = 0
        column_index = 0

        show = None  # If the input variable is password, the text field will need to show *
        for parameter in self.program_text_options:
            if parameter == 'unix_password':
                show = '*'

            # Create the current entry field (label + textbox)
            self.create_entry_field(master, parameter, self.program_text_options[parameter], row_index, column_index,
                                    entry_width=25, show=show, ljust=18)
            row_index = row_index + 1
            show = None

        # Create a checkbutton for each of the file run options. (Create input file, Create run file, Run RASSP, Process output etc...)
        for checkbutton in self.program_checkbuttons:
            self.create_checkbutton(master, checkbutton, self.program_checkbuttons[checkbutton], row=row_index,
                                    column=column_index)
            row_index = row_index + 1

        self.create_button(master, 'windows_dir', 'Windows Directory', 0, 0, sticky='nw')

        self.create_button(master, 'run_rassp', 'Run program!', row_index, column_index,
                           sticky='se', padx=5, pady=5)

    def create_input_file_options_fields(self, master, name, row=0, column=0, padx=0, pady=0, sticky='nw'):

        row_index = 0
        column_index = 0
        entry_width = 7
        for input_file_option in self.input_file_text_options:
            if input_file_option == 'flaw_sizes_a' or input_file_option == 'flaw_sizes_c':
                entry_width = 20
            self.create_entry_field(master, input_file_option, self.input_file_text_options[input_file_option],
                                    row_index, column_index,
                                    entry_width=entry_width, sticky='nw', ljust=22)

            if ('a=c' in self.checkbutton_IntVars and self.checkbutton_IntVars['a=c'].get() == 1 and
                    (input_file_option == 'flaw_sizes_c' or input_file_option == 'c1')):
                self.disable_entry(input_file_option)

            row_index = row_index + 1
            entry_width = 7

        for checkbutton in self.input_file_checkbuttons:
            self.create_checkbutton(master, checkbutton, self.input_file_checkbuttons[checkbutton], row_index,
                                    column_index)
            row_index = row_index + 1

        for var in self.input_file_radiobuttons:
            radio_counter = 0
            for radiobutton in self.input_file_radiobuttons[var]:
                text = self.input_file_radiobuttons[var][radiobutton]
                self.create_radiobutton(master, radiobutton, text, var, radio_counter, row_index, column_index)
                row_index = row_index + 1
                radio_counter = radio_counter + 1
        self.create_text_field(master, 'stf', 'Enter STF (leading spaces not needed):',
                               row_index, column_index, text_width=40, text_height=10)

    def get_crack_case_strings(self):
        combobox_values = []  # List that will be populated with the crack case tite strings

        for crack_case in self.crack_cases:  # Loop through all of the crack cases as the key crack case
            case_title = self.crack_cases_titles[crack_case]  # Get the title string to accompany the crack case
            combobox_values.append(crack_case + ' ' + case_title)  # Append the two and add it to the combobox list
        combobox_values.sort()  # Sort the values (Dictionaries are weird)
        return combobox_values.copy()

    def remove_gen_crack_frames(self):
        for name in self.gen_crack_combo_list:
            self.grid_remove_frame(name)
