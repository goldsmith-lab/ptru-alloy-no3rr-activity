#!/usr/bin/python
from __future__ import with_statement

import sys, re, os


rate = 0
os.system("rm Reaction_rate*")
os.system("rm *cover*")
os.system("rm warnings")
Potential = 96.485 * 0.1
for i in range(26):
    k = i * 20 + 200
    do = k
    for j in range(26):
        try:
            l = j * 20 + 200
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
            f = open(
                "./O_%d__N_%d/range/derivatives.dat"
                % (k, l)
            )
            content = f.readlines()
            f.close()

            x = 0
            y = 0
            m = 0
            for n in range(len(content[1])):
                # print content[1][n]
                if content[1][n] == "	":
                    m = m + 1
                    if m == 2:
                        x = n
                    if m == 3:
                        y = n
            rate = float(content[1][x:y])
            if rate < 0:
                ofile = open("Reaction_rate_NO3", "a")
                ofile.write("%d %d  %E \n" % (k, l, rate))
                ofile.close()

            x = 0
            y = 0
            m = 0
            for n in range(len(content[1])):
                # print content[1][n]
                if content[1][n] == "	":
                    m = m + 1
                    if m == 4:
                        x = n
                    if m == 5:
                        y = n
            rate = float(content[1][x:y])
            ofile = open("Reaction_rate_N2", "a")
            ofile.write("%d %d  %E \n" % (k, l, rate))
            ofile.close()
            x = 0
            y = 0
            m = 0
            for n in range(len(content[1])):
                # print content[1][n]
                if content[1][n] == "	":
                    m = m + 1
                    if m == 5:
                        x = n
                    if m == 6:
                        y = n
            rate = float(content[1][x:y])
            ofile = open("Reaction_rate_N2O", "a")
            ofile.write("%d %d  %E \n" % (k, l, rate))
            ofile.close()
            x = 0
            y = 0
            m = 0
            for n in range(len(content[1])):
                # print content[1][n]
                if content[1][n] == "	":
                    m = m + 1
                    if m == 7:
                        x = n
                    if m == 8:
                        y = n
            rate = float(content[1][x:y])
            ofile = open("Reaction_rate_NO", "a")
            ofile.write("%d %d  %E \n" % (k, l, rate))
            ofile.close()
            x = 0
            y = 0
            m = 0
            for n in range(len(content[1])):
                # print content[1][n]
                if content[1][n] == "	":
                    m = m + 1
                    if m == 8:
                        x = n
                    if m == 9:
                        y = n
            rate = float(content[1][x:y])
            ofile = open("Reaction_rate_NH3", "a")
            ofile.write("%d %d  %E \n" % (k, l, rate))
            ofile.close()
            print "Successfully read from file ./O_%d__N_%d/range/derivatives.dat" % (k, l)
        except IOError:
            print "Sorry, failed to read from file ./O_%d__N_%d/range/derivatives.dat" % (k, l)
########-----------coverage_calculations----------------------------------------------
Potential = 96.485 * 0.1
for i in range(51):
    k = i * 10 + 200
    do = k
    for j in range(51):
        try:
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
            with open(
                "./O_%d__N_%d/range/coverage.dat"
                % (k, l)
            ) as f:
                content = f.readlines()
            #          print content
            a = 0
            b = 0
            c = 0
            d = 0
            e = 0
            f = 0
            g = 0
            h = 0
            x = 0
            y = 0
            m = 0
            o = 0
            p = 0
            q = 0
            for n in range(len(content[1])):
                # print content[1][n]
                if content[1][n] == "	":
                    m = m + 1
                    if m == 9:
                        a = n
                    if m == 10:
                        b = n
                    if m == 11:
                        c = n
                    if m == 12:
                        d = n
                    if m == 13:
                        e = n
                    if m == 14:
                        f = n
                    if m == 15:
                        g = n
                    if m == 16:
                        h = n
                    if m == 17:
                        x = n
                    if m == 18:
                        y = n
                    if m == 19:
                        z = n
                    if m == 20:
                        o = n
                    if m == 21:
                        p = n
                    if m == 22:
                        q = n

            NO3_coverage = float(content[1][a:b])
            H_coverage = float(content[1][b:c])
            NO2_coverage = float(content[1][c:d])
            NO_coverage = float(content[1][d:e])
            N_coverage = float(content[1][e:f])
            NH_coverage = float(content[1][f:g])
            NH2_coverage = float(content[1][g:h])
            NH3_coverage = float(content[1][h:x])
            O_coverage = float(content[1][x:y])
            N2_coverage = float(content[1][y:z])
            N2O_coverage = float(content[1][z:o])
            OH_coverage = float(content[1][o:p])
            H2O_coverage = float(content[1][p:q])
            empty_coverage = float(content[1][q:])
            ofile = open("NO3_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, NO3_coverage))
            ofile.close()
            ofile = open("H_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, H_coverage))
            ofile.close()
            ofile = open("NO2_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, NO2_coverage))
            ofile.close()
            ofile = open("NO_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, NO_coverage))
            ofile.close()
            ofile = open("N_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, N_coverage))
            ofile.close()
            ofile = open("NH_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, N_coverage))
            ofile.close()
            ofile = open("NH2_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, N_coverage))
            ofile.close()
            ofile = open("NH3_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, N_coverage))
            ofile.close()
            ofile = open("O_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, O_coverage))
            ofile.close()
            ofile = open("N2_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, N2_coverage))
            ofile.close()
            ofile = open("N2O_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, N2O_coverage))
            ofile.close()
            ofile = open("OH_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, OH_coverage))
            ofile.close()
            ofile = open("H2O_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, H2O_coverage))
            ofile.close()
            ofile = open("empty_coverage", "a")
            ofile.write("%d %d  %E \n" % (k, l, empty_coverage))
            ofile.close()
            print "Successfully read from file ./O_%d__N_%d/range/coverage.dat" % (k, l)
        except IOError:
            print "Sorry, failed to read from file ./O_%d__N_%d/range/coverage.dat" % (k, l)