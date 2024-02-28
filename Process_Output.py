# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 00:43:57 2021

Module created to do some processing on the RASSP output file and give the user
a slightly modified file which is easier to make a CG graph from. 

The plot_results function is the main aspect of the class (for now) It loops through 
all of the .report files in the windows directory specified by the RASSP object 
passed in. It checks the base file name of the RASSP object against the .report files
to ensure that only the correct groupings of curves are plotted. 

The method outputs a _refined.report that only outputs the flight hours and 
crack length. This makes copy & paste to excel for graphing slightly faster

The method also plots the curves and outputs the plot to the python console. The 
plot may not be quality enough for official documentation, but it gives the user a 
quick view of the curves to make sure they look reasonable. 

When the GUI is implemented, the graph wil hopefully be output to the user's view.


@author: Cade Wooten - 3321153
"""


class Process_Output(object):

    # =============================================================================
    #     Constructor, takes in a RASSP object.
    #     Note* This does not mean that the RASSP program had to be executed on the
    #     unix server. An object can be created without actually running the .ksh file
    #
    #     The report files and refined report files lists are initialized to empty lists
    #     Just for clarity and good practice
    # =============================================================================
    def __init__(self, rassp, flaw_sizes):
        self.rassp = rassp
        self.report_files = []
        self.refined_report_files = []
        self.plots = []
        flaw_sizes.sort()
        self.flaw_sizes = flaw_sizes.copy()

    # =============================================================================
    #     plot_results is where most of the magic happens.
    #     It gathers results files, creates the refined_results files, and plots the
    #     CG curves corresponding to the correct RASSP base_file_name
    # =============================================================================
    def plot_results(self):
        import glob, os
        import numpy as np
        import matplotlib.pyplot as plt

        # Navigate the directory where RASSP report files *Should* be stored
        os.chdir(self.rassp.windows_dir + "Report/")

        # Grab all the files ending in .report and add them to the report_files list
        self.report_files = glob.glob("*.report")

        """
        Filter out any of the files that don't share the same base file name 
        as the RASSP object. The is to ensure only the curves for the same 
        part/ simulation are plotted on the same graph, regardless of other 
        results files that may be in the folder. 
        """
        self.report_files = list(filter(lambda file: self.rassp.base_file_name in file, self.report_files))

        # Make a copy of the report files list for the refined files list, just needed
        # to prevent  index out of bounds errors
        self.refined_report_files = self.report_files.copy()

        # Loop through all of the report files in the folder to process each one individually
        for i in range(len(self.report_files)):

            # If the file is already a refined report file, skip it and return to the start of the loop
            if '_refined.report' in self.report_files[i]:
                continue

            # Change the file name for the new refined report files to _refined.report
            self.refined_report_files[i] = self.report_files[i].replace('.report', '_refined.report')

            # Will be the lists (arrays) that are extracted from each report file
            flights = []
            flight_hours = []
            crack_lengths = []

            # Open the report current .report file to read from
            report_file = open(self.report_files[i], 'r')

            # Open the new refined report file to write to
            refined_file = open(self.refined_report_files[i], 'w')

            # Set the column titles
            refined_file.write('Hours'.rjust(10) + 'Crack_Length'.rjust(15) + '\n')

            # Reads the entire report file and stores it line by line in a list
            lines = report_file.readlines()

            # Initialize indexes for the start and end of block five
            start_index = 0
            end_index = 0

            # This is wildly inefficient. Please change at some point
            # Find out where block five starts and ends (the crack growth data)
            for index, line in enumerate(lines):
                if "BEGIN BLOCK       5" in line:
                    start_index = index + 1
                if "END BLOCK       5" in line:
                    end_index = index - 1

            # If there was no CG data, move on to the next report file
            if start_index == end_index:
                continue

            # Loop through the lines of the report file only containing CG data
            # Probably a more 'pythonic' way to execute this loop, but I went for a
            # Standard for loop
            for j in range(start_index, end_index + 1):
                flight = int(lines[j].split()[0])  # First column of the file is flights
                hours = flight * 3.98  # Calculate the flight hours
                crack_length = float(lines[j].split()[1])  # Get the crack lengths, second column
                flights.append(flight)  # Add this flight # to the list of flights
                flight_hours.append(hours)  # Add the corresponding hours calc to the list of flights
                crack_lengths.append(crack_length)  # Add the crack length to the list
                # Write the outputs to the refined file with some spacing
                refined_file.write(str(int(hours)).rjust(10) + str(round(crack_length, 6)).rjust(10) + '\n')
            # [float(l) for l in crack_lengths]

            # Now loop through that input file and extract the curves for all of the desired starting points
            # We will create a plot for each individual flaw size
            for flaw_size in self.flaw_sizes:
                flaw_size = float(flaw_size)
                reached_crack = False
                index = 0
                current_crack_lengths = []
                current_flight_hours = []
                flight_hours_start = 0

                for k in range(len(crack_lengths)):

                    if crack_lengths[k] >= flaw_size and reached_crack == False:

                        if crack_lengths[k] == flaw_size:
                            flight_hours_start = flight_hours[k]

                        else:
                            flight_hours_start = np.interp(flaw_size, crack_lengths, flight_hours)

                        current_flight_hours.append(0)
                        current_crack_lengths.append(flaw_size)
                        reached_crack = True

                    elif reached_crack == True:
                        current_flight_hours.append(flight_hours[k] - flight_hours_start)
                        current_crack_lengths.append(crack_lengths[k])

                # set the x and y values for plotting
                x_vals = np.array(current_flight_hours)
                y_vals = np.array(current_crack_lengths)

                # Set the label of the series to the filename without .report
                # For a .005 flaw it would be filename_005
                series_label = self.report_files[i].replace('.report', '_') + str(flaw_size)
                self.plots.append((series_label, x_vals, y_vals))  # Add the plot to the list of plots

                # Close the files
                report_file.close()
                refined_file.close()
            # Not entirely sure what is going on here, it sets the axis so you can manipulat them
            f, ax = plt.subplots(1)

        # Actually add the plot list to the plt object
        for plot in self.plots:
            hours = plot[1]
            crack_length = plot[2]
            base_file_name = plot[0]

            ax.plot(hours, crack_length, label=base_file_name)  # Plot the data
            ax.set_ylim(ymin=0)
            ax.set_xlim(xmin=0)

            # Add a data label to the last data point
            ax.text(hours[-1], crack_length[-1],
                    f'{int(round(hours[-1]))} hrs      \n{round(crack_length[-1], 3)}"    ',
                    fontsize=8, ha='right', va='center')

        # Some graph formatting
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xlabel('Flight Hours')
        plt.ylabel('Crack Length')
        num_cols = len(self.plots)
        plt.legend(frameon=False, fontsize='small', loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=num_cols)

        plt.show()  # Actually show the plot

        # Return the lists of data, in case there is a need for it
        return self.plots

    def plot_results_excel(self, worksheet_name=None):
        import xlsxwriter

        # Variable that will be the name of the excel file
        # Includes full filepath so it is strored in the correct directory
        filename = self.rassp.windows_dir + 'Report/' + self.rassp.base_file_name + '_Crack_Curves.xlsx'

        # Define the excel workbook (file)
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet(name=worksheet_name)

        bold = workbook.add_format({'bold': 1})

        # Create the scatter chart - will iteratively add data to the chart below
        scatter_plot = workbook.add_chart({'type': 'scatter',
                                           'subtype': 'smooth'})

        # where to start inserting the columns of data, will increase for each series needed for the plot
        start_column = 1

        # where to start the row for inserting the data, I like it to be down on the page so the graph can be at the top
        start_row = 16

        column_titles = ['Hours', 'Crack Length']

        for series in self.plots:
            # Grab the title, x values, and y values from the plots list.
            # Plots is a list of tuples ie. (title, X_vals_array, y_vals_array)
            series_title = series[0]
            x_vals = series[1]
            y_vals = series[2]

            x_vals_length = len(x_vals)
            y_vals_length = len(y_vals)

            # set the column titles
            worksheet.write_row(start_row, start_column, column_titles, bold)

            # Write the hours and cack length columns
            worksheet.write_column(start_row + 1, start_column, x_vals)
            worksheet.write_column(start_row + 1, start_column + 1, y_vals)

            scatter_plot.add_series({
                'name': series_title,
                'categories': [worksheet_name, start_row + 1, start_column, start_row + x_vals_length, start_column],
                'values': [worksheet_name, start_row + 1, start_column + 1, start_row + y_vals_length, start_column + 1]
            })

            # Increment the column values, gives one blank column between entries
            start_column = start_column + 3

            scatter_plot.set_x_axis({'name': 'Hours',
                                     'major_gridlines': {
                                         'visible': True,
                                         'line': {'color': 'gray', 'transparency': 50}
                                     }
                                     })

            scatter_plot.set_y_axis({'name': 'Crack Length (in)',
                                     'major_gridlines': {
                                         'visible': True,
                                         'line': {'color': 'gray', 'transparency': 50}
                                     }

                                     })

            # scatter_plot.set_style(15)
        scatter_plot.set_legend({'position': 'bottom'})

        scatter_plot.set_chartarea({'border': {'none': True}})

        worksheet.insert_chart('B2', scatter_plot)
        workbook.close()
