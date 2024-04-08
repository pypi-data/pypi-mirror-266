#! /usr/bin/env python3

################################################################################
""" Output the top level directory of the git working tree or return
    an error if we are not in a git working tree.

    Copyright (C) 2017, 2018 John Skilleter

    Licence: GPL v3 or later
"""
################################################################################

import sys
import argparse
import os

from skilleter_thingy import git2 as git

################################################################################

def main():
    """ Main function """

    # Command line parameters

    parser = argparse.ArgumentParser(description='Report top-level directory of the current git working tree.')
    parser.add_argument('-p', '--parent', action='store_true',
                        help='If we are already at the top of the working tree, check if the parent directory is in a working tree and output the top-level directory of that tree.')
    parser.add_argument('-r', '--repo', action='store_true',
                        help='If we are already at the top of the working tree, look for a parent directory with a repo control file (.repo directory or .mrconfig file) and output that directory.')
    parser.add_argument('level', nargs='?', type=int, default=0, help='Number of levels below the top-level directory to report')
    args = parser.parse_args()
    try:
        start_dir = os.getcwd()
    except FileNotFoundError:
        print('Unable to locate current directory')
        sys.exit(1)

    # Try to get the current working tree

    working_tree = git.working_tree(start_dir)

    # If we are in a working tree and also looking for the parent working
    # tree, check if we are at the top of the current tree, and, if so,
    # hop up a level and try again.

    if args.parent and working_tree:
        current_directory = os.getcwd()

        if os.path.samefile(working_tree, current_directory):
            os.chdir('..')

            working_tree = git.working_tree()

    # If we are also looking for a multi-repo control file or directory, and haven't
    # found the git working tree root scan up the tree until we find one.

    if args.repo and not working_tree:
        while True:
            working_tree = os.getcwd()

            if os.path.isdir('.repo') or os.path.isfile('../.mrconfig'):
                break

            if working_tree == '/':
                sys.exit(2)

            os.chdir('..')

    # Output the result, if we have one

    if args.level:
        start = start_dir.split('/')
        working = working_tree.split('/')

        working_tree = os.path.join(working_tree, '/'.join(start[len(working):len(working) + int(args.level)]))

    if working_tree:
        print(working_tree)

################################################################################

def git_wt():
    """Entry point"""

    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    git_wt()
