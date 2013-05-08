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
        pass
    lines.next()

    # Build Udefs lookup: (auto assigned id) => (udef name)
    for line in lines:
        if line == "SUMMARY OF CONSTRAINTS":
            break
        line = line.split()
        if len(line) > 2 and line[2] == "DVAR":
            udefs[int(line[0])] = line[1]
    lines.next()

    # Build Constraints lookup: (auto assigned id) => (constraint name)
    for line in lines:
        if line == "SUMMARY OF TARGETS":
            break
        line = line.split()
        constraints[int(line[0])] = line[1]

    # Build Targets lookup: (auto assigned id) => (target name)
    # TODO: what does ocl.out look like when there are targets with multiple priorities? This *should* still work...
    for line in lines:
        if line == "-----------------------------------------------------":
            break
        line = line.split()
        if len(line) == 6:
            targets[int(line[0])] = line[1]

    # Open lp.out and make the substitutions.
    new_lp_file = open(newlp_fname, "w")
    lines = (line for line in open(lp_fname, "r"))
    for line in lines:
        original = line

        # Perform pattern matching replacement for each type of label
        for prefix, lookup in [("UDEF", udefs),
                               ("CSTR", constraints), 
                               ("TARG", targets),  # name
                               ("SURP", targets),  # surplus
                               ("SLAK", targets)]: # slack
            # Build the appropriate regular expression
            rx_str = "(" + prefix + r"(\d{3}|\d{4})(?!\d))"
            rx = re.compile(rx_str)
            rx_result = rx.findall(line)
            # Perform the replacement for each match. Note: the regular expression is grouped
            # such that each result is of the form (LABEL#, #), for example, if the line
            # contains "UDEF0123" then the result group is ("UDEF0123", "0123").
            for match, id in rx_result:
                replacement = lookup[int(id)]
                # The targets get a special prefix
                if "TARG" in match or "SURP" in match or "SLAK" in match:
                    replacement = prefix + "_" + replacement
                line = string.replace(line, match, replacement)

        new_lp_file.write(line)

if __name__ == "__main__":
    start = time.clock()
    main()
    elapsed = time.clock() - start
    print '%.1f' % elapsed + "s"
