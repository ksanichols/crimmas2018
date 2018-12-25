#!/usr/bin/env python

import itertools
import os
import stat

RED   = "\033[1;31m"
GREEN = "\033[1;32m"
DEFAULT_COLOR = "\033[00m"

def COZY(args):
    return 'print("So cozy")'

def PRINT(args):
    return 'print("{}{}{}")'.format(GREEN, args, DEFAULT_COLOR)

OPERATORS = {
    "COZY" : COZY,
    "PRINT" : PRINT
}

def tokenize(lines):
    return [(line.upper().split(), line, number + 1) \
            for line, number in zip(lines, range(len(lines)))]

def cozy_level_check(line, oline, linum, verbose):
    if len(line) < 2:
        if verbose:
            return ["Syntax error: line too short\n" + \
                    "{}: {}\n".format(linum, oline) +  \
                    "".ljust(len(oline)) + "^^^"]
        else:
            return ["Line {} is BAD.".format(linum)]
    else:
        return []

PREPARSE_ERRORS = [
    cozy_level_check
]

def operator_is_good(parsed_line, oline, linum, verbose):
    operator = parsed_line["operator"]
    if operator not in OPERATORS:
        if verbose:
            return ["Unexpected operator: {}\n".format(operator)]
        else:
            return ["Line {} is BAD.".format(linum)]
    else:
        return []

POSTPARSE_ERRORS = [
    operator_is_good
]


def get_action(parsed_line):
    operator = OPERATORS[parsed_line["operator"]]
    return [operator(parsed_line["args"])]

def parse(line, original_line, linum, verbose=False):
    errors   = []
    warnings = []
    parsed_line = None

    for error_checker in PREPARSE_ERRORS:
        errors += error_checker(line, original_line, linum, verbose)

    if len(errors) == 0:
        operator   = line[0]
        args       = line[1:]
        parsed_line = {"operator": operator, "args" : args}

        for error_checker in POSTPARSE_ERRORS:
            errors += error_checker(parsed_line, original_line, linum, verbose)
    else:
        pass

    return errors, parsed_line

def cozycompile(verbose, f):
    '''Returns a structure of the following format:
    {
        errors   : [string],
        actions  : [void(void)]
    }
    '''
    tokens = tokenize(f)

    errors       = []
    parsed_lines = []

    for line, original_line, linum in tokens:
        e, parsed_line = parse(line, original_line, linum, verbose)
        errors += e
        parsed_lines.append(parsed_line)

    actions = []

    for parsed_line in parsed_lines:
        actions += get_action(parsed_line)

    return {"errors" : errors, "actions" : actions}

def cozylink(actions, outfile):
    outfile.write("#!/usr/bin/env python\n")
    for action in actions:
        outfile.write("{}{}".format(action, "\n"))

def read_files(files):
    in_memory_files = []
    for f in files:
        open_file = open(f)
        in_memory_files.append([line.rstrip('\n') for line in open_file])
    return in_memory_files

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Cozy Compiler v.1.0.1.')
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-o', nargs='?', help="out.", default='cozy.out')
    parser.add_argument('files', metavar='F', nargs='+', help='files.')
    args = parser.parse_args()

    files = read_files(args.files)

    results = [cozycompile(args.v, f) for f in files]

    has_errors = False

    all_actions = []

    for result in results:
        errors = result["errors"]
        for error in errors:
            has_errors = True
            print("{}{}{}".format(RED, error, DEFAULT_COLOR))
        all_actions += result["actions"]

    if not has_errors:
        outfile = open(args.o, 'w')
        cozylink(all_actions, outfile)
        outfile.close()
 
        st = os.stat(args.o)
        os.chmod(args.o, st.st_mode | stat.S_IEXEC)

if __name__ == "__main__":
    main()
