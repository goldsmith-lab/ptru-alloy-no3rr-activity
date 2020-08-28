#!/bin/bash

#
# Author: Ivo Filot
# Date: 21-10-2013
#
# This script generates the input for performing a default MKM simulation in a
# grid specified by the starting points, increments and steps as set out below.
# The default settings are a 51x51 grid with a resolution of 2 kJ/mol.
#
# The workhorse of this script is the Python script called 'geninput.py'. This
# script uses as input the M-CO and M-O2 interaction energies as well as a list of
# MKM parameters as set out in 'default.mkm'. The resulting script is terminated
# with the 'footer.mkm' file. In this file, the precision, temperature range and
# pressure are specified.
#

module load parallel

if [ "$#" -ne 1 ]
then
  echo "Usage: ./generate.sh <directory name>"
  exit 1
fi


startO=200
startN=200

dO=10
dN=10

steps=50 
run=$1

for k in $(seq 0 $steps); do
	let "mO = startO + dO * $k"
	for l in $(seq 0 $steps); do
		let "mN = startN + dN * $l"
		str="O_"$mO"__N_"$mN
		str=`echo $str | sed 's/-/m/g'`
		echo $run/$str
		command="#!/bin/bash
		
		mkdir -p $run/$str
		./Geninput.py  $mO $mN | sed 's/\r//g' > $run/$str/reactions.mkm
		cat $run/$str/reactions.mkm  > $run/$str/input.mkm
		# echo ./worker.sh $run/$str/input.mkm >> commands.txt"
		echo "$command" > "generate-$mO-$mN.sh"				
	done
done

# Now run all of the generate scripts in parallel
chmod u+x generate-*.sh
ls generate-*.sh | parallel --bar -j556 ./{}

rm -rf generate-*.sh
echo "Done generating folders."
