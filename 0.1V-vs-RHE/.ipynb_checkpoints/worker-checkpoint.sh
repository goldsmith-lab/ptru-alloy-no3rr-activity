#!/bin/bash

# Worker script to process a single MKMCXX run
FOLDER=$(dirname $1)

# Go to the subdirectory and run the simulation
cd "$FOLDER"

# Don't run simulation if results already exist
if [ -d "./run" ] ; then
    echo "Results already found in $FOLDER/run; skipping."
else

    # Using Shifter (e.g., on NERSC Cori)
    shifter --image=samueldy/mkmcxx:2.7.0 mkmcxx -i input.mkm

    # Using Docker
    # docker run --volume "$(pwd)":/home/working_dir --workdir /home/working_dir samueldy/mkmcxx:2.7.0 mkmcxx -i input.mkm

    echo "Done with $FOLDER"
fi
