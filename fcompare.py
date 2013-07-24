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
parser.add_argument('folder1', metavar='F1', type=str, nargs=1,
help='folder 1')
parser.add_argument('folder2', metavar='F2', type=str, nargs=1,
help='folder 2')
parser.add_argument('--cutoff', '-c', dest='cutoff', default=0.6,
type=float, help='cutoff value [0, 1] for defining the\
file name similarity (default: 0.6)')
parser.add_argument('--pattern', '-p', dest='pattern',
default='([a-zA-Z]{1}[0-9]{1,2}[a-zA-Z]{1}$)',
help='pattern (regexp) to be used for file name \
matching (default: \
"([a-zA-Z]{1}[0-9]{1,2}[a-zA-Z]{1}$)"')
parser.add_argument('--extension', '-e', dest='extension', default='.tif',
help='extension of the files to be matched \
(default: .tif)')
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
 
print('\nUsing file name matching cutoff value {0}\n'.format(args.cutoff))
 
# Counters for matched and unmatched files
exact_match = 0
similar_match_one = 0
similar_match_many = 0
unmatched = []
 
if len(files1) != len(files2):
print('WARNING: number of files in folders differs ({0} and \
{1})'.format(len(files1), len(files2)))
else:
for _file1 in files1:
_file1_token = _file1.replace(args.extension, '')
 
# First, try almost an exact match (disregarding the pattern
# provided)
m = re.search(args.pattern, _file1_token)
if m is not None:
_file1_token = _file1_token.replace(m.groups()[0], '')
# FIXME: trailing underscore is still retained
exact_matches = get_close_matches(_file1_token, files2,
cutoff=1.0)
if exact_matches:
exact_match += 1
# Then try similar matches
matches = get_close_matches(_file1_token, files2,
cutoff=args.cutoff)
if matches:
if len(matches) == 1:
print('INFO: following match found for file:\n \
<ofile> {0}'.format(_file1))
print(' <match> {0}'.format(matches[0]))
print('\n')
similar_match_one += 1
if len(matches) > 1:
print('WARNING: multiple matches found for file:\n \
<ofile> {0}'.format(_file1))
pprint.pprint(matches)
print('\n')
similar_match_many += 1
else:
print('WARNING: no candidate match for file: \n \
<ofile> {0}\n'.format(_file1))
unmatched.append(_file1)
 
print('*' * 50)
print('Number of <{0}> files in folders: {1}'.format(args.extension,
len(files1)))
print('Exact matches using pattern {0}:'.format(args.pattern))
print(' exact: {0}'.format(exact_match))
print('File name matching cutoff value {0}'.format(args.cutoff))
print(' similar (one match): {0}'.format(similar_match_one))
print(' similar (multiple matches): {0}'.format(similar_match_many))
print(' no match: {0}'.format(len(unmatched)))
if unmatched:
print('\nUnmatched files:')
pprint.pprint(unmatched)
 
if __name__ == '__main__':
sys.exit(main())
