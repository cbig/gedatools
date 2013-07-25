#!/usr/bin/env python

""" Utility script to compare whether the content of 2 folders appear to be
same.

Similarity is based on simple file name matching.
"""

import argparse
from difflib import get_close_matches
import glob
import os
import pprint
import re
import sys


def main():

    parser = argparse.ArgumentParser(description='Compare the content of two \
                                                  folders.')
    # Positional arguments
    parser.add_argument('folder1', metavar='F1', type=str, nargs=1,
                        help='folder 1')
    parser.add_argument('folder2', metavar='F2', type=str, nargs=1,
                        help='folder 2')
    # Options
    parser.add_argument('--cutoff', '-c', dest='cutoff', default=None,
                        type=float, help='cutoff value [0, 1] for defining the\
                                          file name similarity (default: None, use exact spp name)')
    parser.add_argument('--extension', '-e', dest='extension', default='.tif',
                        help='extension of the files to be matched \
                        (default: .tif)')
    parser.add_argument('--output', '-o', dest='output', default=None,
                        help='print unmatched files to a file')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', default=False,
                        help='verbose reporting (print also matches, default: False)')

    args = parser.parse_args()

    folder1 = args.folder1[0]
    folder2 = args.folder2[0]

    # Check the inputs
    if not os.path.exists(folder1):
        print('ERROR: folder {0} does not exist'.format(folder1))
        exit(1)
    if not os.path.exists(folder2):
        print('ERROR: folder {0} does not exist'.format(folder2))
        exit(1)

    files1 = glob.glob(os.path.join(folder1, '*' + args.extension))
    files1 = [os.path.basename(_file) for _file in files1]
    files2 = glob.glob(os.path.join(folder2, '*' + args.extension))
    files2 = [os.path.basename(_file) for _file in files2]

    if args.cutoff:
        print('\nUsing file name matching cutoff value {0}\n'.format(args.cutoff))

    # Counters for matched and unmatched files
    exact_match = 0
    similar_match_one = 0
    similar_match_many = 0
    unmatched = []

    if len(files1) != len(files2):
        print('WARNING: number of files in folders differs ({0} and {1})'.format(len(files1), len(files2)))

    for _file1 in files1:
        _file1_token = _file1.replace(args.extension, '')

        matches = {}

        # If cutoff value is provided, use similarity matching
        if args.cutoff:
            # Then try similar matches
            matches[_file1] = get_close_matches(_file1_token, files2, cutoff=args.cutoff)
        else:
            # First, extract the feature name token (such as species name) and see
            # if any of the files in the comparison set are the same.
            # See if the feature name is found in the file token
            p = re.compile('[A-Z]{1}[a-z]+[A-Z]{1}[a-z]+')
            m = re.search(p, _file1_token)
            if m:
                _file1_token = m.group()
            else:
                print('WARNING: Could not find "_GenusSpecies[...]_" pattern in filename {0}'.format(_file1))
                continue
            # See if any of the filenames in files2 contains the feature name (_file1_token)
            for filename in files2:
                if _file1_token in filename:
                    matches[_file1] = filename
        if len(matches) == 1:
            if args.verbose:
                print('INFO: following match found for file:\n <ofile> {0}'.format(_file1))
                print(' <match> {0}'.format(matches[_file1]))
                print('\n')
            exact_match += 1
        elif len(matches) > 1:
            print('WARNING: multiple matches found for file: {0}'.format(_file1))
            pprint.pprint(matches)
            similar_match_many += 1
        else:
            print('WARNING: no candidate match for file: {0}'.format(_file1))
            unmatched.append(_file1)

    print('*' * 50)
    print('Number of <{0}> files in folder F1: {1}'.format(args.extension,
                                                           len(files1)))
    print('Matches using feature name:')
    print(' match: {0}'.format(exact_match))
    if args.cutoff:
        print('File name matching cutoff value {0}'.format(args.cutoff))
        print(' similar (one match): {0}'.format(similar_match_one))
        print(' similar (multiple matches): {0}'.format(similar_match_many))
    print(' no match: {0}'.format(len(unmatched)))
    if unmatched and args.verbose:
        print('\nUnmatched files:')
        pprint.pprint(unmatched)

    if args.output and len(unmatched) > 0:
        print('Printing unmatched files into file {0}'.format(args.output))
        with open(args.output, 'w') as ofile:
            for _file in unmatched:
                ofile.write('{0}\n'.format(_file))


if __name__ == '__main__':
    sys.exit(main())
