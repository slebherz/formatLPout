"""
    Make lp.out more human readable by substituting the automatically generated
    numbers for udefs, constraints, and targets with the user entered labels.
"""

import string
import re
import time

def main():

    # TODO: assumes we're running in the run directory. Perhaps the run path should be parsed from Directry.nam?
    ocl_fname = "OCL.out"
    lp_fname  = "lp.out"
    newlp_fname = "lp_readable.out"
    
    """
        1. Build the mappings for targets, constraints, and udefs.
            In OCL.out, each of these items has an associated number, and the number
            is what is printed in lp.out. We will grab both of them in OCL.out
            so we can replace the numbers in lp.out with the names.
    """
    # Used to store the mappings:
    udefs = {}
    constraints = {}
    targets = {}

    lines = (line.strip() for line in open(ocl_fname, "r") if len(line.strip()) > 0)

    # Chew through the file until we get to the UDEFs
    while lines.next() != "SUMMARY OF UDEFS":
        #debug_file.write(line)
        pass

    lines.next()

    print lines
    # Grab the udefs
    for line in lines:
        if line == "SUMMARY OF CONSTRAINTS":
            break
        line = line.split()
        if len(line) > 2 and line[2] == "DVAR":
            udefs[int(line[0])] = line[1]
    lines.next()

    # Grab the constraints
    for line in lines:
        if line == "SUMMARY OF TARGETS":
            break
        line = line.split()
        constraints[int(line[0])] = line[1]

    # Grab the targets
    # TODO: what does ocl.out look like when there are targets with multiple priorities? This *should* still work...
    for line in lines:
        if line == "-----------------------------------------------------":
            break
        if line[0].isdigit():
            line = line.split()
            targets[int(line[0])] = line[1]

    
    # Now, open lp.out and make the substitutions.
    udef3_rx = re.compile(r"UDEF\d\d\d")
    udef4_rx = re.compile(r"UDEF\d\d\d\d")
    cstr3_rx = re.compile(r"CSTR\d\d\d")
    cstr4_rx = re.compile(r"CSTR\d\d\d\d")
    tgt0_rx  = re.compile(r"TARG\d\d\d")
    tgt1_rx  = re.compile(r"SURP\d\d\d")
    tgt2_rx  = re.compile(r"SLAK\d\d\d")
    
    new_lp_file = open(newlp_fname, "w")
    lines = (line for line in open(lp_fname, "r"))
    for line in lines:
        original = line

        # udef 3-digit replacement
        udef_result = udef3_rx.findall(line) 
        for match in udef_result:
            try:
                line = string.replace(line, match, udefs[int(match[-3:])])
                
            except KeyError:
                #print "3-digit error non-DVAR UDEF found in lp.out"
                #print original
                pass
                
        # udef 4-digit replacement
        udef_result = udef4_rx.findall(line) 
        for match in udef_result:
            try:
                line = string.replace(line, match, udefs[int(match[-4:])])
                
            except KeyError:
                #print "4-digit error non-DVAR UDEF found in lp.out"
                #print original
                pass
                
        # constraint 3-digit replacement
        cstr_result = cstr3_rx.findall(line) 
        for match in cstr_result:
            try:
                line = string.replace(line, match, constraints[int(match[-3:])])
                
            except KeyError:
                #print "3-digit error ONSTRAINT found in lp.out"
                #print original
                pass
                
        # constraint 4-digit replacement
        cstr_result = cstr4_rx.findall(line) 
        for match in cstr_result:
            try:
                line = string.replace(line, match, constraints[int(match[-4:])])
                
            except KeyError:
                #print "4-digit error ONSTRAINT found in lp.out"
                #print original
                pass

        # constraint replacement
        #cstr_result = cstr_rx.findall(line) 
        #for match in cstr_result:
        #    line = string.replace(line, match, match[:4] + "_" + constraints[int(match[-3:])])

        # target (name) replacement
        tgt0_result = tgt0_rx.findall(line) 
        for match in tgt0_result:
            line = string.replace(line, match, match[:4] + "_" + targets[int(match[-3:])])

        # target (surplus) replacement
        tgt1_result = tgt1_rx.findall(line) 
        for match in tgt1_result:
            line = string.replace(line, match, match[:4] + "_" + targets[int(match[-3:])])

        # target (slack) replacement
        tgt2_result = tgt2_rx.findall(line) 
        for match in tgt2_result:
            #print targets
            #print int(match[-3:])
            line = string.replace(line, match, match[:4] + "_" + targets[int(match[-3:])])

        new_lp_file.write(line)

        """
        #
        # Check the replacement
        #
        if line != original:
            print "original: " + original
            print "\n"
            print "readable: " + line
            print "\n\n"
            raw_input("")
        """

    """    
    #
    # Check the mapping
    #
    print ""
    print "UDEFS: " + str(len(udefs))
    for item in sorted(udefs.iteritems()):
        print '%04d' % item[0], item[1]
    
    print ""
    print "CONSTRAINTS: " + str(len(constraints))
    for item in sorted(constraints.iteritems()):
        print '%03d' % item[0], item[1]

    print ""
    print "TARGETS: " + str(len(targets))
    for item in sorted(targets.iteritems()):
        print '%03d' % item[0], item[1]
    """
        
if __name__ == "__main__":
    start = time.clock()
    main()
    elapsed = time.clock() - start
    print '%.1f' % elapsed + "s"
