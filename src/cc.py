#!/usr/bin/env python

import itertools
import os
import stat
import random
import sys
import time

RED   = "\033[1;31m"
GREEN = "\033[1;32m"
DEFAULT_COLOR = "\033[00m"

def make_colorizer(c):
    def colorizer(word):
        return "{}{}{}".format(c, word, DEFAULT_COLOR)
    return colorizer

red   = make_colorizer(RED)
green = make_colorizer(GREEN)

crimmas_colorizers = [ red, green ]

def random_color(word):
    return random.choice(crimmas_colorizers)(word)

def get_pretty_printer(line):
    return """
for word in {}:
    color = random.choice(crimmas_colorizers)
    for _ in range(5):
        sys.stdout.write(color(random_case(word)))
        sys.stdout.flush()
        sys.stdout.write("\\r")
        time.sleep(0.1)
""".format(line)

GOOD_WORDS = [
    "HOME",
    "COZY",
    "BOOP",
    ":3",
    ":>",
    "'V'",
    ".^.",
    "<:",
    "'W'",
    "HUG",
    "MERRY",
    "CHRISTMAS"
]

def parse(line, original_line, linum, verbose=False):
    errors   = []

    cozy_count = 0
    for word in line:
        if word.upper() == "COZY":
            cozy_count += 1
        if not word.upper() in GOOD_WORDS:
            if verbose:
                errors.append("Unexpected token recieved: {}\n".format(word)
                              + "Did you mean {}?".format(random.choice(GOOD_WORDS)))
            else:
                errors.append("Unexpected token recieved: {}".format(word))

    if cozy_count < 3:
        if verbose:
            errors.append("The following line is insufficiently cozy:\n"
                          + "{}: {}\n".format(linum, original_line)
                          + "^^^".rjust(len(original_line)))
        else:
            errors.append("Coziness deduction failure on line {}.".format(linum))

    return errors, cozy_count

def tokenize(lines):
    return [(line.upper().split(), line, number + 1) \
            for line, number in zip(lines, range(len(lines)))]

def cozycompile(verbose, f, f_name):
    '''Returns a structure of the following format:
    {
        errors   : [string]
    }
    '''
    tokens = tokenize(f)

    errors       = []
    parsed_lines = []
    actions      = []

    total_num_cozies = 0

    for line, original_line, linum in tokens:
        e, num_cozies = parse(line, original_line, linum, verbose)
        errors += e
        total_num_cozies += num_cozies
        if len(e) == 0:
            actions.append(get_pretty_printer(line))

    COZY_COEFFICIENT = 195239.43
    if total_num_cozies * COZY_COEFFICIENT < 1000000:
        errors.append("{} is insufficiently cozy!!! Cozy level {} < 1000000".format(f_name,
            total_num_cozies * COZY_COEFFICIENT))

    return {"errors" : errors,
            "num_cozies" : num_cozies,
            "f_name" : f_name,
            "actions" : actions}

def read_files(files):
    in_memory_files = []
    for f in files:
        open_file = open(f)
        in_memory_files.append(([line.rstrip('\n') for line in open_file], f))
    return in_memory_files

def write_program(outfile, all_actions):
    boiler_plate = """#!/usr/bin/env python
import random
import sys
import time

RED   = "\033[1;31m"
GREEN = "\033[1;32m"
DEFAULT_COLOR = "\033[00m"

def make_colorizer(c):
    def colorizer(word):
        return "{}{}{}".format(c, word, DEFAULT_COLOR)
    return colorizer

red   = make_colorizer(RED)
green = make_colorizer(GREEN)

crimmas_colorizers = [ red, green ]

def random_case(word):
    return "".join([random.choice([l.upper(), l.lower()]) for l in word])
"""
    outfile.write(boiler_plate)
    for action in all_actions:
        outfile.write(action)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Cozy Compiler v.1.0.1.')
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-o', nargs='?', help="out.", default='cozy.out')
    parser.add_argument('files', metavar='F', nargs='+', help='files.')
    args = parser.parse_args()

    files = read_files(args.files)

    results = [cozycompile(args.v, f, name) for f, name in files]

    has_errors = False

    all_actions = []

    for result in results:
        errors = result["errors"]
        if len(errors) > 0:
            has_errors = True
            print(result["f_name"])
            for error in errors:
                print("{}{}{}".format(RED, error, DEFAULT_COLOR))
        else:
            all_actions += (result["actions"])

    if not has_errors:
        outfile = open(args.o, 'w')
        write_program(outfile, all_actions)
        outfile.close()
 
        st = os.stat(args.o)
        os.chmod(args.o, st.st_mode | stat.S_IEXEC)

if __name__ == "__main__":
    main()
