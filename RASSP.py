# -*- coding: utf-8 -*-
"""
The RASSP module / class serves as a way to access the Unix server and run a 
RASSP simulation from the windows environment. The user will input their UNIX
username and password which will allow the program to SSH into the server 

The user specifies a file location on the windows machine where the .input, 
.spec (for FSFT) and .ksh files are located. They will also provide the name of a folder
to create on the Unix server. The folder will be located in their user folder 
directory. ie: /u257/ry219e/RASSP_Automation/ 
This folder will house all of the RASSP material, but will not need to be accessed
by the user. Any information in the RASSP folder will be removed before the simulation is run 

The program will run through all of the input files in the specified windows folder
and output the results into the same folder once the RASSP program is complete

The connection attempt to Unix will time out after five seconds. 
*I have never had it take more than three attempts to connect, recommend doing a 
loop of three try: statements to connect. If that doesn't work there may be a larger
connection issue

The RASSP instance can also create the ksh file using the template created by
Josiah Lund. It is currently stored in Cade Wooten's user folder at 
// LOCATION
@TODO Move it to the server 


@author: Cade Wooten - 3321153
"""


class RASSP(object):
    # Parameters that are not expected to change, inherited by every
    # instance of the RASSP Class
    hostname = 'b1b-sw-3000.cs.boeing.com'
    port = 22

    # Constructor
    def __init__(self, username, password, unix_dir, windows_dir, base_file_name, spec_file_name='', run_file_name=''):

        # Username and password used to log in to UNIX server
        self.username = username
        self.password = password

        self.spec_file_name = spec_file_name
        self.run_file_name = run_file_name
        # Folder to conduct RASSP analysis on server, does not need to be already created
        self.unix_dir = unix_dir

        # Full file path where input files live
        self.windows_dir = windows_dir

        self.base_file_name = base_file_name

        # Just to initialize all of the variables, aren't set until rassp_execute
        self.inputFileNames = None
        self.runFileNames = None
        self.specFileNames = None

        self.reportFileNames = None
        self.printFileNames = None

        self.num_input_files = None

    # Connects to UNIX server and runs the RASSP program
    def rassp_execute(self, timeout=5):
        import paramiko, stat, os, glob
        # from scp import SCPClient
        os.chdir(self.windows_dir)
        self.inputFileNames = glob.glob("*.input")  # Search for all input files
        self.runFileNames = glob.glob("*.ksh")  # Search for all ksh (JCL) files
        self.specFileNames = glob.glob("*.spec")  # Search for all spectrum files

        # If there is not a Print and Report folder in the windows directory, create them
        # That is where the print and report files will be stored
        if not os.path.isdir(self.windows_dir + "Print/"):
            os.mkdir(self.windows_dir + "Print/")

        if not os.path.isdir(self.windows_dir + "Report/"):
            os.mkdir(self.windows_dir + "Report/")

        # Filter out any of the input files that do not contain the base file name
        base_name_input_files = []
        for input_file in self.inputFileNames:
            if self.base_file_name in input_file:
                base_name_input_files.append(input_file)

        # Set the instance variable input file names to the list of filtered file names
        self.inputFileNames = base_name_input_files.copy()

        # Create copies of the input file lists for the report and print files
        self.reportFileNames = self.inputFileNames.copy()
        self.printFileNames = self.inputFileNames.copy()

        self.num_input_files = len(self.inputFileNames)

        # Give the report and print files the correct file extension
        for i in range(self.num_input_files):
            self.reportFileNames[i] = self.reportFileNames[i].replace('.input', '.report')
            self.printFileNames[i] = self.printFileNames[i].replace('.input', '.print')

        # Establish ssh client
        ssh_client = paramiko.SSHClient()

        # Automatically add key if it is missing
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Let the user know you are trying to connect via ssh
        # TODO Needs to be rewitten using exceptions
        print('Connecting...')
        ssh_client.connect(hostname=self.hostname, port=self.port, username=self.username,
                           password=self.password, timeout=timeout)
        print('Connection established')  # Successful connection

        # Makes file transfer a little faster - tweeks with some parameters
        ssh_client.get_transport().window_size = 3 * 1024 * 1024

        # Connect to file system
        ftp_client = ssh_client.open_sftp()

        # Check if the desired analysis folder exists, if not create it
        dirList = ftp_client.listdir('./')
        dirFound = False

        for folder in dirList:
            # If the folder does exist, delete the contents
            if self.unix_dir == folder + "/":
                file_list = ftp_client.listdir('./' + self.unix_dir)
                for file in file_list:
                    ftp_client.remove('./' + self.unix_dir + file)
                dirFound = True

        # If the file doesn't exist, make it
        if (dirFound == False):
            ftp_client.mkdir(self.unix_dir)

        # Have a good day : )

        # Change the unix working directory - makes the code down below cleaner
        ftp_client.chdir(("./" + self.unix_dir))

        # Move a copy of each input file to the UNIX directory
        for inputFile in self.inputFileNames:
            ftp_client.put(self.windows_dir + inputFile, inputFile)
            print(inputFile + ' Transferred')

        # Move a copy of each spectrum file (with the right base file name) to the UNIX directory
        for specFile in self.specFileNames:
            if self.spec_file_name in specFile:
                ftp_client.put(self.windows_dir + specFile, specFile)
                print(specFile + ' Transferred')

        # Move a copy of each run file to the UNIX directory
        for runFile in self.runFileNames:
            if self.run_file_name in runFile:
                ftp_client.put(self.windows_dir + runFile, runFile)
                print(runFile + ' Transferred')

                # Change the permissions of the run file to allow execution
                ftp_client.chmod(runFile, stat.S_IXOTH)

        # Execute the run files. All execution code must be in one method call - weird feature of the exec_command method
        # The weird perl -p mumbo jumbo is to format the ksh file correctly,
        # It is changed from ascii to binary when transfered which causes problems in UNIX
        print('Starting RASSP \n \n')
        stdin, stdout, stderr = ssh_client.exec_command("cd " + self.unix_dir + "/ \n chmod 777 " + self.run_file_name +
                                                        "\n perl -p -i -e 's/\r//g' " + self.run_file_name + "\n" + self.run_file_name)

        # Print the unix console output to the user, also ensures the program stalls until RASSP run is complete
        # TODO print this to a text file or something, will make it easier to see if something went wrong
        # Could also print to the GUI once that is running
        print(stdout.read().decode().strip() + '\n \n')
        print('RASSP run complete')

        # Copy the output files from the UNIX server location to the specified user folder on windows
        for i in range(self.num_input_files):
            ftp_client.get(self.reportFileNames[i], self.windows_dir + "Report/" + self.reportFileNames[i])
            ftp_client.get(self.printFileNames[i], self.windows_dir + "Print/" + self.printFileNames[i])

        print('File transfer complete')
        ftp_client.close()
        ssh_client.close()

        # Creates a ksh file, needs a .spec file and a ksh template to point to

    # Really only works for a CARDS run right now
    def create_ksh(self, output_name, spec_file_type, spec_file='/sw05nfs064/lund/rassp_databases/v1.3.0/integral',
                   element_location='fif',
                   ksh_template_location="//Sw.nos.boeing.com/b1bdata/data300$/groups/structures_3/users_data/Wooten"
                                         "/00_Tools/RASSP_Automation/Util/"):
        ksh_template_location = ksh_template_location + spec_file_type + '_template.ksh'
        template = open(ksh_template_location, 'r')  # open the template file to read
        template_lines = template.readlines()  # Read all lines and store in list

        # loop through the template file line by line
        for index, line in enumerate(template_lines):

            # Change the ft31 and ft28 file locations if using a cardn spec
            if spec_file_type == 'CARDN':
                if line.startswith('RASSP_db_dir'):
                    template_lines[index] = line.strip() + spec_file + '\n'
                if line.startswith('loads_ft31_file'):
                    template_lines[index] = line.strip() + element_location + '\n'
                if line.startswith('spec_ft11_file'):
                    template_lines[index] = line.strip() + element_location + '\n'

            # Check for unix spectrum file clallout
            elif 'spec_ft11_file=/' in line and spec_file_type == 'CARDS':
                # Replace the tempplate line with the correct line
                spec_file = 'spec_ft11_file=/u257/' + self.username + '/' + self.unix_dir + spec_file + '\n'
                template_lines[index] = spec_file

        # Create a .ksh file in the windows directory and add copy over all of the lines
        # From the template (with the needed replaced values)
        ksh_file = open(self.windows_dir + output_name, 'w', encoding='utf-8')
        ksh_file.writelines(template_lines)

        # Close the files
        template.close()
        ksh_file.close()
