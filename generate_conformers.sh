#!/usr/bin/env bash

# Non-posix compliant tools used in this script:
# gnu sed (gsed)
# gnu split (gsplit)
# grep
# obabel
# confab

# abort on nonzero exit status
set -o errexit 
# abort on unbound variable
set -o nounset
# dont hide errors within pipes
set -o pipefail

# Asks user for the starting conformer file in the xyz file format
echo
echo Enter your starting conformer \(xyz file\):
read -e filename
echo

# Exits script if file isn't found
if [ ! -f ${filename} ]; then
        echo File "${filename}" does not exist.
        echo Exiting script.
	echo
        exit
fi

# Makes tmpfiles/ directory if it doesn't already exist
if [ ! -d ./tmpfiles ]; then
	mkdir ./tmpfiles
fi

# Conformer library generation using obabel
if [ -f ./tmpfiles/${filename%%.*}_conf_library.xyz ]; then # Overwrite protection for existing conformer library 
	echo Previously generated list of conformers detected under filename "./tmpfiles/${filename%%.*}_conf_library.xyz" 
	echo Exiting script to avoid file overwrite.
	echo
	exit
else # Generates conformer library
	echo Generating conformer library in "./tmpfiles/${filename%%.*}_conf_library.xyz" ...
	echo
	obabel "${filename}" -O "./tmpfiles/${filename%%.*}_conf_library.xyz" --confab --verbose
	echo
	echo Done.
	echo
fi

n=$(grep -c "xyz" "./tmpfiles/${filename%%.*}_conf_library.xyz") # Every occurence of "xyz" in the conformer library is summed as n, where n is the total number of conformers
nn=$((${n}-1))

# Conformers are given index numbers
# Script isn't written to handle more than 9999 conformers, but subsequent elif terms could be added
if [ ${n} -lt 10 ]; then
        echo Conformers will be assigned indexes 00000 through 0000${nn} 
	echo
elif [ ${n} -ge 10 -a ${n} -lt 100 ]; then
        echo Conformers will be assigned indexes 00000 through 000${nn}
	echo
elif [ ${n} -ge 100 -a ${n} -lt 1000 ]; then
	echo Conformers will be assigned indexes 00000 through 00${nn}
	echo
elif [ ${n} -ge 1000 -a ${n} -lt 10000 ]; then
        echo Conformers will be assigned indexes 00000 through 0${nn}
	echo
elif [ ${n} -ge 10000 -a ${n} -lt 100000 ]; then
        echo Conformers will be assigned indexes 00000 through ${nn}
	echo
else
	echo Total conformer number has exceeded 99999 - which this script cannot handle.
	echo If you insist on moving forward, this script will need to be edited.
	echo Exiting script.
	echo
	exit
fi

# confab first searches for rotatable bonds and then applies torsion rules to bonds systematically to generate conformers
# confab only recognizes acyclic single bonds where both atoms are connected to at least two non-hydrogen atoms, and neither atom is sp-hybridized
# It may be necessary to generate several starting conformers from which to build a conformer library based on intuition or PE scans, and thus the user may need some control over index number assignment
echo WARNING: Existing conformers with the same index numbers will be overwritten if a new starting index is not declared.
echo Do you wish to start at an index other than 0 \(y/n\)?
read assignindex
echo

if [ "${assignindex}" = y ]; then
	echo Please enter an integer value for your new starting index:
        read index
	echo
	re="^[0-9]+$" # sets up regular expression for only positive integers
	while ! [[ ${index} =~ ${re} ]]; do 
		echo ERROR: Please enter an integer value.
		echo Try again or press CTRL+C to exit:
		read index
	done
	# if ! [[ ${index} =~ ${re} ]]; then # script fails if user input isn't a positive integer
	# 	echo Error: You entered something other than an integer value.
	# 	echo Exiting script.
	# 	echo
	# 	exit
	# fi
else
        index=0 
fi

# Generates the ./geometries/unoptimized directory if it doesn't already exist
# mkdir doesn't work on multiplie nested directories that haven't been made yet - hence two loops are needed
if [[ ! -d ./geometries/ && ! -d ./geometries/unoptimized/ ]]; then
	mkdir ./geometries
	mkdir ./geometries/unoptimized/
elif [ ! -d ./geometries/unoptimized/ ]; then
	mkdir ./geometries/unoptimized/
else
	:
fi

# Splites the conformer library file into separate conformer files in the .xyz format
if [ ${index} -eq 0 ]; then # assumes starting index of 0
	cd ./geometries/unoptimized/
        echo Generating separate conformer .xyz files from conformer library...
        gsplit -n "${n}" -a 5 -d --additional-suffix=.xyz "../../tmpfiles/${filename%%.*}_conf_library.xyz" conf
	cd ../../
        echo Done.
        echo
else # uses user specified starting index
	cd ./geometries/unoptimized/
        echo Generating separate conformer .xyz files from conformer library...
        gsplit -n "${n}" -a 5 --numeric-suffixes="${index}" --additional-suffix=.xyz "../../tmpfiles/${filename%%.*}_conf_library.xyz" conf
	cd ../../
        echo Done.
        echo
fi

# Template .inp and .pbs file generation for opt, freq, anharm, and hf calculations
if [ ! -d ./template_inppbs/ ]; then
	mkdir ./template_inppbs/
fi

# Sets up regular expression parameters to include only real numbers 
re="^[+-]?[0-9]+([.][0-9]+)?$"

# Overwrite protection for existing opt.inp file
if [ ! -f ./template_inppbs/template_opt.inp ]; then
	cd ./template_inppbs/
	echo Enter molecular charge: # allow user to specify charge
	read charge
	echo
	if ! [[ ${charge} =~ ${re} ]]; then # uses regular expression to check input is a real number
		echo Error: You did not enter a number.
		echo Exiting script.
		cd ../
		echo
		exit
	fi
	echo Enter molecular multiplicity: # allow user to specify multiplicity
	read mult
	echo
	if ! [[ ${mult} =~ ${re} ]]; then # uses regular expression to check input is a real number
		echo Error: You did not enter a number.
		echo Exiting script.
		cd ../
		echo
		exit
	fi
	echo '%NProcShared=12
%mem=12GB
%rwf=/tmp/PLACEHOLDER_opt/,-1
%chk=/tmp/PLACEHOLDER_opt/PLACEHOLDER_opt.chk
#T B3LYP/6-311++G(2d,2p) OPT(Tight) scf(tight)

 Gaussian09 opt calc of PLACEHOLDER using B3LYP/6-311++G(2d,2p)
' >> template_opt.inp # writes header to opt.inp file
	echo "${charge} ${mult}" >> template_opt.inp # writes charge and multiplicity to opt.inp file
	echo "COORDS GO HERE

" >> template_opt.inp # sets up a space for molecular coordinates to go
	cd ../
fi

# freq.inp file setup
if [ ! -f ./template_inppbs/template_freq.inp ]; then
	cd ./template_inppbs/
	echo '%NProcShared=12
%mem=12GB
%rwf=/tmp/PLACEHOLDER_freq/,-1
%chk=/tmp/PLACEHOLDER_freq/PLACEHOLDER_freq.chk
#T B3LYP/6-311++G(2d,2p) Freq(HPModes) scf(tight)  

 Gaussian09 freq calc of PLACEHOLDER using B3LYP/6-311++G(2d,2p)
' >> template_freq.inp
	echo "${charge} ${mult}" >> template_freq.inp
	echo "COORDS GO HERE

" >> template_freq.inp
	cd ../
fi

# anharm.inp file setup
if [ ! -f ./template_inppbs/template_anharm.inp ]; then
	cd ./template_inppbs/
	echo '%NProcShared=12
%mem=12GB
%rwf=/tmp/PLACEHOLDER_anharm/,-1
%chk=/tmp/PLACEHOLDER_anharm/PLACEHOLDER_anharm.chk
#T B3LYP/6-311++G(2d,2p) Freq(Anharmonic) scf(tight)  

 Gaussian09 anharm calc of PLACEHOLDER using B3LYP/6-311++G(2d,2p)
' >> template_anharm.inp
	echo "${charge} ${mult}" >> template_anharm.inp
	echo "COORDS GO HERE

" >> template_anharm.inp
	cd ../
fi

# hf.inp file setup
if [ ! -f ./template_inppbs/template_hf.inp ]; then
	cd ./template_inppbs/
	echo '%NProcShared=12
%mem=12GB
%rwf=/tmp/PLACEHOLDER_hf/,-1
%chk=/tmp/PLACEHOLDER_hf/PLACEHOLDER_hf.chk
#P HF/6-31g* OPT(Tight) scf(tight)

 Gaussian09 HF opt of PLACEHOLDER_hf using HF/6-31g*
' >> template_hf.inp
	echo "${charge} ${mult}" >> template_hf.inp
	echo "COORDS GO HERE

" >> template_hf.inp
	cd ../
fi

# Overwrite protection for existing opt.pbs file
if [ ! -f ./template_inppbs/template_opt.pbs ]; then
	cd ./template_inppbs/
	echo '#!/bin/bash
#SBATCH --output="PLACEHOLDER_opt.out"
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --export=ALL
#SBATCH --time=0-24:00:00
#SBATCH --error=PLACEHOLDER_opt.err

hostname

# Create scratch directory here:
test -d /tmp/PLACEHOLDER_opt || mkdir -v /tmp/PLACEHOLDER_opt

# Activate Gaussian:
#export g09root=/usr/local/packages/gaussian
#. $g09root/g09/bsd/g09.profile
module load gaussian

which g09

g09 < PLACEHOLDER_opt.inp > PLACEHOLDER_opt.out

# Copy checkpoint file from local scratch to working directory after job completes:
cp -pv /tmp/PLACEHOLDER_opt/PLACEHOLDER_opt.chk .

# Clean up scratch:
rm -rv /tmp/PLACEHOLDER_opt
' >> template_opt.pbs # writes header to opt.pbs file
	cd ../
fi

cd ./template_inppbs/
# Unlike the .inp files, the .pbs files are all essentially the same
# Copies of opt.pbs are made for anharm, freq, and hf calculations
cp template_opt.pbs template_anharm.pbs
cp template_opt.pbs template_freq.pbs
cp template_opt.pbs template_hf.pbs
# Copied .pbs files undergo substitutions where necessary
gsed -i 's/opt/anharm/g' template_anharm.pbs
gsed -i 's/short/long/g' template_anharm.pbs
gsed -i 's/24/96/g' template_anharm.pbs
gsed -i 's/opt/freq/g' template_freq.pbs
gsed -i 's/opt/hf/g' template_hf.pbs

