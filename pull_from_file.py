
""" PULL GAUSSIAN QUOTE """

for outfile in $(find . \( ! -regex '.*/\..*' \) -type f -name "*.out"); do
	if grep -q "Normal termination of Gaussian" "${outfile}"; then
		echo "${outfile}" Terminated normally.
		quote=$(gsed -n "/\\\@/,/Job cpu time/p" "${outfile}")
		quote="${quote%Job*}"
		quote="${quote##*\@}"
		echo "${quote}" >> ~/gaussianquotes.txt
		echo
	else
		echo "${outfile}" Did NOT terminate normally.
		echo
	fi
done

""" PULL OPTIMIZED ENERGY """

if ! grep -q "Normal termination of Gaussian 09 at" "${f}"; then
	echo WARNING: "${f##*/}" did not terminate normally!
	echo Exiting script.
	echo
	exit
else
	a=$(gsed -n "/GINC/,/\@/p" ${f})
	a=$(echo ${a//[$'\t\r\n ']})
	a=${a#*HF=}
	a=${a%\\RMSD*}
	echo The energy of your optimized structure is: "${a}" Hartrees
	echo
fi

""" PULL STANDARD ORIENTATION """

echo
echo WARNING: This script will not correctly write a new .xyz file if your molecule contains atoms larger than Calcium.
echo 'Enter (y) to continue, or (n) to exit script:'
read q

if ! grep -q "Normal termination of Gaussian 09 at" "${f}"; then
	echo "${f}" did not terminate normally.
	echo Do you still want to try to pull the last set of coordinates from the .out file?
	echo 'Enter (y) to attempt coordinate extraction, or (n) to exit script:'
	read q
	echo
	if ! [ ${q} = 'y' ]; then
		echo Exiting script.
		echo
		exit 0
	else
		opt=no
	fi
fi

# Pulls the energy of the optimized structure to be reported at the end of the script
if ! [ ${opt} = 'no' ]; then
	a=$(gsed -n "/GINC/,/\@/p" ${f})
	a=$(echo ${a//[$'\t\r\n ']})
	a=${a#*HF=}
	a=${a%\\RMSD*}
fi

# Optimized coordinate extraction
# Combining the following three commands trips the non zero exit error, so it is necessary to split the tac, gsed, and tac commands into three separate lines
# tac "${f}" | gsed '/Rotational\ constants/,$!d;/Standard\ orientation\:/q' | tac >> ./tmp/tmp.txt # Copies optimized geometry table from .out file
tac "${f}" >> ./tmp/tmp.txt
gsed '/Rotational\ constants/,$!d;/Standard\ orientation\:/q' ./tmp/tmp.txt >> ./tmp/tmp2.txt
tac ./tmp/tmp2.txt >> ./tmp/tmp3.txt

gsed -i '1,5d' ./tmp/tmp3.txt # removes the first five lines of the table
gsed -i '$d' ./tmp/tmp3.txt # removes the last two lines of the table
gsed -i '$d' ./tmp/tmp3.txt
awk '{print $2, $4, $5, $6}' ./tmp/tmp3.txt >> ./tmp/tmp4.txt # pulls out the 2nd, 4th, 5th, and 6th columns

# calculate_rmsd cannot read the atom identity from its atomic mass number (unlike Gaussian or Avogadro)
# The gsed statements below replace the atomic numbers with their letter abbreviation
# H comes last because if this gsed command came before Ne (for instance), it would replace the "1" in "10" with an "H"
gsed -i '1,$s/^20/Ca/' ./tmp/tmp4.txt # From line 2 to the end of the file, if the atomic number is found in the first character of a line replace it with its letter abbreviation
gsed -i '1,$s/^19/K\ /' ./tmp/tmp4.txt
gsed -i '1,$s/^18/Ar/' ./tmp/tmp4.txt
gsed -i '1,$s/^17/Cl/' ./tmp/tmp4.txt
gsed -i '1,$s/^16/S\ /' ./tmp/tmp4.txt
gsed -i '1,$s/^15/P\ /' ./tmp/tmp4.txt
gsed -i '1,$s/^14/Si/' ./tmp/tmp4.txt
gsed -i '1,$s/^13/Al/' ./tmp/tmp4.txt
gsed -i '1,$s/^12/Mg/' ./tmp/tmp4.txt
gsed -i '1,$s/^11/Na/' ./tmp/tmp4.txt
gsed -i '1,$s/^10/Ne/' ./tmp/tmp4.txt
gsed -i '1,$s/^9/F/' ./tmp/tmp4.txt
gsed -i '1,$s/^8/O/' ./tmp/tmp4.txt
gsed -i '1,$s/^7/N/' ./tmp/tmp4.txt
gsed -i '1,$s/^6/C/' ./tmp/tmp4.txt
gsed -i '1,$s/^5/B/' ./tmp/tmp4.txt
gsed -i '1,$s/^4\ /Be/' ./tmp/tmp4.txt
gsed -i '1,$s/^3\ /Li/' ./tmp/tmp4.txt
gsed -i '1,$s/^2\ /He/' ./tmp/tmp4.txt
gsed -i '1,$s/^1/H/' ./tmp/tmp4.txt

