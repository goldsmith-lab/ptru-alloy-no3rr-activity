#!/usr/bin/python

import sys, re, os

# Open file to hold commands for GNU parallel
with open("commands.txt", "w") as f:


    Potential = 96.485 * 0.1
    for i in range(52):
        k = i * 10 + 200
        do = k
        for j in range(51):
            l = j * 10 + 200
            dn = l
            if (
                -0.234 * do - 0.054 * dn + 197.505 < 0
                or -0.451 * do - 0.080 * dn + 339.82 < 0
                or 0.250 * do + 0.063 * dn - 11.29 < 0
                or -1.725 * do + 1.887 * dn + 158.24 < 0
                or -1.049 * do + 0.742 * dn + 211.11 < 0
                or -0.115 * do + 0.256 * dn + 39.17291 + Potential / 2 < 0
                or -0.137 * do + 0.238 * dn + 64.162525 + Potential / 2 < 0
                or 0.093 * do + 0.016 * dn + 71.97781 + +Potential / 2 < 0
                or 0.348 * do - 0.028 * dn - 76.71 + +Potential / 2 < 0
                or 0.021 * do + 0.210 * dn - 8.78 + Potential / 2 < 0
            ):
                continue
            if (
                0.593 * do + 0.064 * dn - 127.75 < 0
                or -0.036 * do + 0.628 * dn - 101.89 < 0
                or 0.561 * do - 0.043 * dn - 107.97 < 0
                or 0.186 * do - 1.697 * dn + 956.65 < 0
                or -0.040 * do + 0.294 * dn + 82.49 < 0
                or -0.574 * do + 1.237 * dn - 54.51 < 0
                or 0.330 * do - 0.591 * dn + 267.166965 - Potential / 2 < 0
                or -0.231 * do - 0.227 * dn + 383.720845 - Potential / 2 < 0
                or 0.007 * do - 0.369 * dn + 282.218625 - Potential / 2 < 0
                or 0.050 * do - 0.378 * dn + 273.73 - Potential / 2 < 0
                or -0.298 * do - 0.046 * dn + 237.64 - Potential / 2 < 0
            ):
                continue

            command = (
                "./worker.sh ./O_%d__N_%d/input.mkm \n"
                % (k, l)
            )
            f.write(command)
            print "Wrote command for EO = %d, EN = %d" % (k, l)

            # Write command to file

            # exitcode = os.system(
            #         " shifter --image=samueldy/mkmcxx:2.15.3 mkmcxx -i ./O_%d__N_%d/input.mkm"
            #     % (k, l)
            # )
            # os.system("mv SEQUENCERUN_*  O_%d__N_%d" % (k, l))
