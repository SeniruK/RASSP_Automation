#!/bin/ksh
# Written by Josiah Lund
# 3/28/2017

# To use, place this file in the directory containing the inputs you wish to run,
# set directory/file paths below, and execute.

# set working directory and load/spectrum files
loads_ft31_file=/sw05nfs064/rassp/B_1_FSFT_Wing/LOADS_FT31/WING_ANALYTICAL                                        # path to unit 31 loads database
spec_ft28_file=/u002/rassp/B_1_FSFT/SPECTRUM_FT28 
spec_ft11_file=/u257/ry219e/Dry_Bay_Panels_New/Xf37.spec

working_dir=$PWD
report_path=${working_dir}

# Do not change anything below this line
#------------------------------------------------------------------------------#
anal_point=*.input

#check if required files exist
error=0;
echo
if [ ! -f $spec_ft11_file ]; then
	echo 'Error: file 11 not found'
	error=1;
fi
if [ ! -f $spec_ft28_file ]; then
	echo 'Error: file 28 not found'
	error=1;
fi
if [ ! -f $loads_ft31_file ]; then
	echo 'Error: file 31 not found'
	error=1;
fi
if [ ! -f $anal_point ]; then
	echo 'Error: analysis point not found'
	error=1;
fi
if [ $error -ne 0 ]; then
	echo
	echo 'Exiting for error(s). No analysis has been performed.'
	echo 'Correct above errors and re-run'
	exit
fi

for x in $anal_point
	do
	x=`basename $x .input`
	echo $x
	
	# create links to input files
	ln -s ${spec_ft11_file}                     ftn11
	ln -s ${spec_ft28_file}                     ftn28
	ln -s ${loads_ft31_file}                    ftn31

	ln -s ${working_dir}/${x}.input             ftn55

	# create links to output files
	#cp   ${working_dir}/run.ksh                      ftn41
	cp  ${working_dir}/${x}.input                            ftn41
	ln -s ${working_dir}/${x}.print             ftn56
	ln -s ${working_dir}/${x}.report            ftn42

	# run RASSP
	/u257/str_codes/programs_hp/rassp/rassp_5000_spec

	# append error summary to end of print file
	cat ftn01 >> $working_dir/${x}.print
	
	# clean up run directory (jcl directory)
	rm ftn*
	rm core
	
	echo "RASSP run complete"
	grep FLIGHTS ${working_dir}/${x}.report 
	grep "MAXIMUM COMBINATION" ${working_dir}/${x}.print
	grep "MAXIMUM GROSS" ${working_dir}/${x}.print
	grep "MAXIMUM NET" ${working_dir}/${x}.print
	grep "AFTER 1000 MISSIONS CRACK GROWTH IS ZERO" ${working_dir}/${x}.print
	echo
done
