#!/usr/bin/python

import sys,re


### print header information and read in variables
print '----------------------------------'
print 'Running ! ',sys.argv[0]
print '----------------------------------'

if(len(sys.argv) != 3):
        print 'I need two parameters!!, stopping...'
        print '------------------------------------'
        exit()

do = float(sys.argv[1])
dn = float(sys.argv[2])
#print 'Adjusting M-C with', str(dmco), 'kJ/mol.'
#print 'Adjusting M-O with', str(dmo), 'kJ/mol.'
#print '----------------------------------'

### load default file
with open('input.mkm') as f:
    content = f.readlines()
##
##--------### modify parameters------------------------
# rules
# -----
#
Potential = 96.485 * 0.1

dNO  = -(-0.66*dn+100.3444)
dN2  = -(-0.20*dn+42.45)
dN2O = -(-0.57*dn+243.14)
dH2O = -(-0.12*do+15.44)
dNH3 = -(-0.13*dn-16.40245)

dNO3 = (-0.52*do+259.54465)-Potential
dH2 =  (-0.41*dn+164.0245)
dHaquf = (-0.41*dn+164.0245)/2 + Potential


dNO3_diss_f = -0.234*do - 0.054*dn + 197.505
dNO3_diss_b =  0.593*do + 0.064*dn - 127.75

dNO2_diss_f = -0.451*do - 0.080*dn + 339.82
dNO2_diss_b = -0.036*do + 0.628*dn - 101.89

dNO_diss_f = -0.652*do - 0.238*dn + 526.12
dNO_diss_b =  0.561*do - 0.043*dn -107.97

dN2_f = 0.250*do + 0.063*dn - 11.29
dN2_b = 0.186*do - 1.697*dn + 956.65

dN2O_f = -1.725*do + 1.887*dn + 158.24
dN2O_b = -0.040*do + 0.294*dn + 82.49

dN2O_diss_f = -1.049*do + 0.742*dn + 211.11
dN2O_diss_b = -0.574*do + 1.237*dn - 54.51

dNHf = -0.115*do + 0.256*dn + 39.17291 + Potential/2
dNHb =  0.330*do - 0.591*dn + 267.166965 - Potential/2

dNH2f = -0.137*do + 0.238*dn + 64.162525 + Potential/2
dNH2b = -0.231*do - 0.227*dn + 383.720845 - Potential/2

dNH3f = 0.093*do + 0.016*dn + 71.97781 +Potential/2
dNH3b = 0.007*do - 0.369*dn + 282.218625-Potential/2

dOHf = 0.348*do - 0.028*dn - 76.71+Potential/2
dOHb = 0.050*do - 0.378*dn + 273.73-Potential/2

dH2Of =  0.021*do + 0.210*dn - 8.78+Potential/2
dH2Ob = -0.298*do - 0.046*dn + 237.64-Potential/2

# Set substitution counters to 0
Number= len(content)
ads=0
Ef=0
Eb=0
for i in range(Number):
      match = False
      if "HK; {NO}" in content[i]:
          match=True
          ads=dNO
          content[i]= 'HK; {NO}        +        {*}    =>   {NO*};             1e-19;          28;              2.87;          2;      1;                    %fe3; 1 \n '  %ads
          sys.stdout.write(content[i]);
          continue
      if "HK; {N2}" in content[i]:
          match=True
          ads=dN2
	  content[i]= 'HK; {N2}        +        {*}    =>   {N2*};             1e-19;          28;              2.87;          2;      1;                    %fe3;1 \n '  %ads
          sys.stdout.write(content[i]);
          continue
      if "HK; {N2O}" in content[i]:
          match=True
          ads=dN2O
          content[i]= 'HK; {N2O}        +        {*}    =>   {N2O*};           1e-19;          44;               350;          2;      1;                    %fe3;1 \n '  %ads
          sys.stdout.write(content[i]);
          continue
      if "HK; {H2O}" in content[i]:
          match=True
          ads=dH2O
          content[i]= 'HK; {H2O}       +        {*}    =>  {H2O*};             1e-19;          18;                 2;          2;      1;                    %fe3;1 \n' %ads
          sys.stdout.write(content[i]);
          continue
      if "HK; {NH3}" in content[i]:
          match=True
          ads=dNH3
          content[i]= 'HK; {NH3}       +        {*}    =>  {NH3*};             1e-19;          17;                10;          3;      1;                    %fe3;1  \n' %ads
          sys.stdout.write(content[i]);
          continue
      if "AR; {NO3-}" in  content[i]:
          match=True
          Ef= dNO3
          Eb= 0
          
          # Invert barriers if one is negative
        #   if Ef < 0:
        #       Ef, Eb = Eb, -Ef
          
          content[i]='AR; {NO3-}      +        {*}    => {NO3*}                   ;   1e13;   1e13;    %fe3;   %fe3;  1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; {NO3*}" in  content[i]:
          match=True
          Ef=dNO3_diss_f
          Eb=dNO3_diss_b
          content[i]='AR; {NO3*}      +        {*}    => {NO2*}       +       {O*};   1e13;   1e13;    %fe3;   %fe3;  1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; {NO2*}" in  content[i]:
          match=True
          Ef=dNO2_diss_f
          Eb=dNO2_diss_b
          content[i]='AR; {NO2*}      +        {*}    => {NO*}        +       {O*};   1e13;   1e13;    %fe3;  %fe3;  1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; {NO*}" in  content[i]:
          match=True
          Ef=dNO_diss_f
          Eb=dNO_diss_b
          content[i]='AR; {NO*}       +        {*}    => {N*}         +       {O*};   1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; 2{N*}" in  content[i]:
          match=True
          Ef=dN2_f
          Eb=dN2_b
          content[i]='AR; 2{N*}                       => {N2*}        +        {*};   1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; 2{NO*}" in  content[i]:
          match=True
          Ef=dN2O_f
          Eb=dN2O_b
          content[i]='AR; 2{NO*}                      => {N2O*}       +       {O*};   1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; {N2O*}" in  content[i]:
          match=True
          Ef=dN2O_diss_f
          Eb=dN2O_diss_b
          content[i]='AR; {N2O*}      +       {*}     => {N2*}        +       {O*};   1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue

      if "AR; {N*}" in  content[i]:
          match=True
          Ef=dNHf
          Eb=dNHb
          content[i]='AR; {N*}        +       {Haqu}  => {NH*}                    ;   1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; {NH*}" in  content[i]:
          match=True
          Ef=dNH2f
          Eb=dNH2b
          content[i]='AR; {NH*}       +       {Haqu}  => {NH2*}                   ;   1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; {NH2*}" in  content[i]:
          match=True
          Ef=dNH3f
          Eb=dNH3b
          content[i]='AR; {NH2*}      +       {Haqu}  => {NH3*}                   ;   1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue

      if "AR; {O*}" in  content[i]:
          match=True
          Ef=dOHf
          Eb=dOHb
          content[i]='AR; {O*}        +       {Haqu}  => {OH*}                    ;   1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; {OH*}" in  content[i]:
          match=True
          Ef=dH2Of
          Eb=dH2Ob
          content[i]='AR; {OH*}       +       {Haqu}  => {H2O*}                   ;   1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; {Haqu}" in  content[i]:
          match=True
          Ef=dHaquf
          Eb=0
          
          # Invert barriers if one is negative
        #   if Ef < 0:
        #       Ef, Eb = Eb, -Ef
          
          content[i]='AR; {Haqu}+{*}   => {H*}                                  ;     1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue
      if "AR; {H2}" in  content[i]:
          match=True
          Ef=dH2
          Eb=0
          
          # Invert barriers if one is negative
        #   if Ef < 0:
        #       Ef, Eb = Eb, -Ef
          
          content[i]='AR; {H2} +2{*}                      =>   2{H*}            ;     1e13;   1e13;    %fe3;   %fe3; 1 \n' %(Ef,Eb)
          sys.stdout.write(content[i]);
          continue

      if match is False:
                sys.stdout.write(content[i]);
