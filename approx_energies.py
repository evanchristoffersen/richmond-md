# Need to figure out how to import the obabel C++ library

""" PREVIOUS BASH MEAT

	for f in ./geometries/unoptimized/*.xyz; do
		approxenergy="$(obenergy -h -ff GAFF "${f}" 2>/dev/null | grep "TOTAL ENERGY")"
		approxenergy="${approxenergy% *}"
		approxenergy="${approxenergy##* }"
		f="${f%.*}"
		f="${f##*/}"
		echo "${f}","${approxenergy}" >> ./tmpfiles/tmp/gaff_tmp.csv
	done & for f in ./geometries/unoptimized/*.xyz; do
		approxenergy2="$(obenergy -h -ff MMFF94 "${f}" 2>/dev/null | grep "TOTAL ENERGY")"
		approxenergy2="${approxenergy2% *}"
		approxenergy2="${approxenergy2##* }"
		f="${f%.*}"
		f="${f##*/}"
		echo "${f}","${approxenergy2}" >> ./tmpfiles/tmp/mmff94_tmp.csv
	done & for f in ./geometries/unoptimized/*.xyz; do
		approxenergy3="$(obenergy -h -ff UFF "${f}" 2>/dev/null | grep "TOTAL ENERGY")"
		approxenergy3="${approxenergy3% *}"
		approxenergy3="${approxenergy3##* }"
		f="${f%.*}"
		f="${f##*/}"
		echo Analyzing conformer "${f}"...
		echo "${f}","${approxenergy3}" >> ./tmpfiles/tmp/uff_tmp.csv
	done & wait
	
	echo Done.
	
	# sorts all normalized results in order of increasing conformer energy
	sort -k2 -n -t, ./tmpfiles/tmp/gaff_tmp.csv >> ./tmpfiles/gaff_results.csv
	sort -k2 -n -t, ./tmpfiles/tmp/mmff94_tmp.csv >> ./tmpfiles/mmff94_results.csv
	sort -k2 -n -t, ./tmpfiles/tmp/uff_tmp.csv >> ./tmpfiles/uff_results.csv

"""
