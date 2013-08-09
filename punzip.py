#!/usr/bin/env python

""" Module for extracting multiple zipfiles at the same time.
"""

import argparse
import functools
import logging
import multiprocessing
import os.path
import pprint
import re
import sys
import time
import zipfile

LOG_LEVELS = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING,
              'error': logging.ERROR}


def extract(zipname, overwrite=False):
    """ Extract a single zipfile.
    """
    start_time = time.time()
    logger = multiprocessing.get_logger()

    zfile = zipfile.ZipFile(zipname)
    root = os.path.dirname(zipname)

    # Create a counter to give feedback on progress
    files_extracted = 0
    files_skipped = 0
    nfiles = len(zfile.namelist())
    increment = nfiles / 10
    m = 1

    # Define a name for the curretn process
    multiprocessing.current_process().name = os.path.split(zipname)[-1]

    logger.info('Starting to decompress {0} files.'.format(nfiles))

    #pprint.pprint(zfile.namelist())

    for name in zfile.namelist():
        # FIXME: does not handle more than 1 level folder hierarchy properly
        path_items = name.split('/')
        if len(path_items) == 1:
            # Having only 1 item means there is no folder structure at all. Use zip name to create folder.
            dirname = zipname.replace('.zip', '')
            filename = path_items[0]
        elif len(path_items) == 3:
            # If the first and the second item are the same, then the root folder structure is
            # duplicated, e.g.:
            # IUCN_AmphibiansCBIGClassification_r15o/IUCN_AmphibiansCBIGClassification_r15o/IUCN_AcanthixalusSonjae_r15o.tfw
            if path_items[0] == path_items[1]:
                dirname = path_items[1]
                filename = path_items[2]
            else:
                logger.error('Don\'t know how to deal with folder depths >= 2')
                return(1)
        elif len(path_items) > 3:
            logger.error('Don\'t know how to deal with folder depths >= 2')
            return(1)
        else:
            (dirname, filename) = os.path.split(name)

        # Filename may be empty in case only dirname is provided
        try:
            if dirname and filename:
                dirname = os.path.join(root, dirname)
      
                filename = os.path.join(dirname, filename)
                if not os.path.exists(dirname):
                    logger.debug('Creating folder {0}'.format(dirname))
                    os.mkdir(dirname)
                if os.path.exists(filename):
                    if overwrite:
                        logger.debug('Overwrite on, replacing file {0}.'.format(filename))
                        fd = open(filename, 'w')
                        fd.write(zfile.read(name))
                        fd.close()
                        files_extracted += 1
                    else:
                        logger.debug('File {0} exists and overwrite is off, skipping.'.format(filename))
                        files_skipped += 1
                else:
                    logger.debug('Decompressing {0} on {1}'.format(filename, dirname))
                    fd = open(filename, 'w')
                    fd.write(zfile.read(name))
                    fd.close()
                    files_extracted += 1

                if files_extracted >= m * increment:
                    logger.info('{0}/{1} files processed'.format(files_extracted + files_skipped, nfiles))
                    m += 1

        except IOError, e:
            logger.error('Error extracting zipfile: {0}'.format(e))
    stop_time = time.time()
    logger.info('Finished. Extracted {0} and skipped {1} files from {2} in {3} seconds.'.format(files_extracted,
                                                                                                files_skipped,
                                                                                                os.path.basename(zipname),
                                                                                                round(stop_time - start_time, 3)))
    return(0)


def main():
    parser = argparse.ArgumentParser(description='Extract multiple zip files in folder tree.')
    # Args
    parser.add_argument('root', metavar='FOLDER', type=str, nargs=1, help='Root folder')
    # Options
    parser.add_argument('--jobs', '-j', dest='jobs', type=int, default=None,
                        help='number of concurrent jobs (subprocesses, default: 1')
    parser.add_argument('--list', '-l', dest='list', action='store_true', default=False,
                        help='list all zip files found in folder tree and exit')
    parser.add_argument('--logging', '-L', dest='logging', type=str, default='info',
                        choices=LOG_LEVELS.keys(),
                        help='logging level used')
    parser.add_argument('--overwrite', '-o', dest='overwrite', action='store_true', default=False,
                        help='overwrite existing files')
    parser.add_argument('--pattern', '-p', dest='pattern',
                        help='regex pattern for matching particular files')

    args = parser.parse_args()

    multiprocessing.log_to_stderr(LOG_LEVELS[args.logging])
    logger = multiprocessing.get_logger()

    folder = args.root[0]
    zipfiles = []

    if args.pattern:
        logger.info('Using file matching pattern: \'{0}\''.format(args.pattern))

    logger.info('Scanning the folder tree, this could take a while...')

    for root, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if args.pattern:
                p = re.compile(args.pattern)
                m = p.search(filename)
            else:
                m = True
            if m and filename.endswith('.zip'):
                zipfiles.append(os.path.abspath(os.path.join(root, filename)))

    if args.list:
        logger.info('{0} files found in the folder tree:'.format(len(zipfiles)))
        for _file in zipfiles:
            logger.info('{0}'.format(_file))
        sys.exit(0)

    if args.jobs > multiprocessing.cpu_count():
        logger.warning('Assigning more jobs ({0}) than available CPUs ({1})'.format(args.jobs,
                                                                                    multiprocessing.cpu_count()))
    if args.jobs > len(zipfiles):
        logger.warning('Assigning more jobs ({0}) than zipfiles found ({1}), setting jobs to {2}'.format(args.jobs, len(zipfiles), len(zipfiles)))
        args.jobs = len(zipfiles)

    if args.jobs is None:
        # Safe number of jobs is half of the available CPU capacity
        safe_njobs = multiprocessing.cpu_count() / 2
        if len(zipfiles) < safe_njobs:
            args.jobs = len(zipfiles)
            logger.info('Number of jobs not defined for {0} zipfiles, assigning {0} jobs.'.format(len(zipfiles),
                                                                                                  args.jobs))
        else:
            args.jobs = safe_njobs
            logger.info('Number of jobs not defined for {0} zipfiles, assigning a safe number of {0} jobs.'.format(len(zipfiles),
                                                                                                                   args.jobs))

    assert args.jobs > 0, 'ERROR: number of jobs must be a positive integer'

    # Set up the worker pool
    start_time = time.time()
    pool = multiprocessing.Pool(processes=args.jobs)
    # Multitprocessing map only takes 1 argument, so we have to use partials
    pool.map(functools.partial(extract, overwrite=args.overwrite), zipfiles)
    stop_time = time.time()
    logger.info('Finished all extractions in {0} seconds.'.format(round(stop_time - start_time, 3)))
    return(0)


if __name__ == '__main__':
    main()
