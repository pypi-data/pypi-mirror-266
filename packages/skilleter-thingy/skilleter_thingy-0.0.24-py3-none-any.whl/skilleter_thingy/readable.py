#! /usr/bin/env python3

################################################################################
""" Pipe for converting colour combinations to make them readable

    Defaults to making things readable on a light background but has the
    option to make things readable on a dark background or for removing
    colours altogether
"""

# TODO: Not sure it works properly as a pipe
# TODO: Error handling in file I/O

################################################################################

import sys
import argparse
import tempfile
import os
import re
import filecmp
import shutil

from skilleter_thingy import tidy
from skilleter_thingy import files

################################################################################

TF_OBJECTS_CHANGED_END = 'Terraform detected the following changes made outside of Terraform since the last "terraform apply":'
TF_IGNORE_MSG = 'Unless you have made equivalent changes to your configuration, or ignored the relevant attributes using ignore_changes, the following plan may include actions to undo or respond to these changes.'

TF_REFRESHING_AND_READING = re.compile(r'.*: (?:Refreshing state\.\.\.|Reading\.\.\.|Read complete after ).*')
TF_FINDING_AND_INSTALLING = re.compile(r'- (?:Finding .*[.]{3}|Installing .*[.]{3}|Installed .*)') 

TF_HAS_CHANGED = re.compile(r'  # .* has changed')
TF_READ_DURING_APPLY = re.compile(r' +# [-a-z_.0-9\[\]]+ will be read during apply')
TF_UNCHANGED_TAG = re.compile(r' +".*" += +".*"')

TF_OBJECTS_CHANGED = 'Note: Objects have changed outside of Terraform'
TF_UNCHANGED_HIDDEN = re.compile(r' +# \(\d+ unchanged (?:attribute|block|element)s? hidden\)')

################################################################################

def parse_command_line():
    """ Parse, check and sanitise the command line arguments """

    parser = argparse.ArgumentParser(description='Read from standard input and write to standard output modifying ANSI colour codes en-route.')

    parser.add_argument('-l', '--light', action='store_true', help='Modify colours for a light background (the default)')
    parser.add_argument('-d', '--dark', action='store_true', help='Modify colours for a dark background')
    parser.add_argument('-n', '--none', action='store_true', help='Remove all colour codes')
    parser.add_argument('-t', '--tidy', action='store_true',
                        help='Remove colour codes and stuff that typically occurs in log files causing diffs, but is of no particular interest (e.g. SHA1 values, times, dates)')
    parser.add_argument('-s', '--strip-blank', action='store_true', help='Strip all blank lines')
    parser.add_argument('-D', '--debug', action='store_true', help='Replace colours with debug information')
    parser.add_argument('-o', '--out', action='store_true', help='Output to standard output rather than overwriting input files')
    parser.add_argument('-O', '--dir', action='store', default=None, help='Store output files in the specified directory (creating it if it doesn\'t exist)')
    parser.add_argument('-a', '--aws', action='store_true', help='Remove AWS resource IDs')
    parser.add_argument('-T', '--terraform', action='store_true', help='Clean Terraform plan/apply log files')
    parser.add_argument('files', nargs='*', default=None, help='The files to convert (use stdin/stout if no input files are specified)')

    args = parser.parse_args()

    # Can't do more than one transformation

    if args.light + args.dark + args.none + args.debug > 1:
        print('ERROR: Only one colour conversion option can be specified')
        sys.exit(1)

    if args.tidy and (args.light or args.dark or args.debug):
        print('ERROR: The tidy and colour conversion options cannot be specified together')
        sys.exit(1)

    # Default to doing cleanup - removing colour codes, times,

    if not args.light and not args.dark and not args.tidy and not args.strip_blank and not args.terraform:
        args.strip_blank = args.none = args.tidy = args.terraform = True

    # Terraform option also removes ANSI, etc.

    if args.terraform:
        args.strip_blank = args.tidy = args.none = True

    # Create the output directory, if required

    if args.dir and not os.path.isdir(args.dir):
        os.mkdir(args.dir)

    return args

################################################################################

def cleanfile(args, infile, outfile):
    """ Clean infile, writing to outfile.
        Returns True if any changes were made. """

    # Set if we are ignoring a block of adata

    ignore_until = False

    prev_line = None

    ignore_until = None
    collection = []

    # Read, process and write stdin to stdout, converting appropriately

    for data in infile:
        # Remove the trailing newline

        if data[-1] == '\n':
            data = data[:-1]

        # Strip trailing whitespace

        data = data.rstrip()

        # Do colour code conversion

        if args.debug:
            clean = tidy.debug_format(data)
        elif args.light:
            clean = tidy.convert_ansi(data, True)
        elif args.dark:
            clean = tidy.convert_ansi(data, False)
        elif args.none:
            clean = tidy.remove_ansi(data)
        else:
            clean = data

        # Do tidying

        if args.tidy:
            clean = tidy.remove_sha256(clean)
            clean = tidy.remove_sha1(clean)
            clean = tidy.remove_times(clean)

            if not args.light and not args.dark:
                clean = tidy.remove_ansi(clean)

        # Remove AWS ID values

        if args.aws:
            clean = tidy.remove_aws_ids(clean)

        # Do things with Terraform log data

        if args.terraform:
            if TF_HAS_CHANGED.fullmatch(clean):
                ignore_until = '    }'

            elif TF_READ_DURING_APPLY.fullmatch(clean):
                ignore_until = '    }'

            elif clean == TF_OBJECTS_CHANGED:
                ignore_until = TF_OBJECTS_CHANGED_END

            elif TF_UNCHANGED_HIDDEN.fullmatch(clean):
                clean = None

            elif clean == TF_IGNORE_MSG:
                clean = None

            elif TF_UNCHANGED_TAG.fullmatch(clean):
                clean = None

            elif TF_REFRESHING_AND_READING.match(clean) or TF_FINDING_AND_INSTALLING.fullmatch(clean):
                # Collect a block of non-deterministically-ordered data

                collection.append(clean)
                clean = None

            elif collection:
                # If we collected a block, write it out in sorted order

                collection.sort()
                for entry in collection:
                    outfile.write(entry)
                    outfile.write('\n')

                collection = []

        # Write normal output, skipping >1 blank lines

        if clean is not None and not ignore_until:
            if clean != '' or prev_line != '':
                outfile.write(clean)
                outfile.write('\n')

            prev_line = clean

        # Clear the ignore flag if we've hid the end marker of the block

        if ignore_until and clean == ignore_until:
            ignore_until = None

################################################################################

def main():
    """ Main code """

    # Process command line options

    args = parse_command_line()

    # We are either processing 1 or more files, or just piping stdin to stdout

    if args.files:
        try:
            for filename in args.files:
                with open(filename, 'rt') as infile:

                    # Either write to stdout or to a temporary file

                    if args.out:
                        outfile = sys.stdout
                        outfile_name = None
                    else:
                        outfile = tempfile.NamedTemporaryFile(mode='wt+', delete=False)
                        outfile_name = outfile.name

                    cleanfile(args, infile, outfile)

                    if outfile_name:
                        outfile.close()

                # If we wrote to an output file then do something

                if outfile_name:
                    if args.dir:
                        # Writing to a directory - just move the output file there unconditionally

                        shutil.move(outfile_name, os.path.join(args.dir, os.path.basename(filename)))

                    elif not filecmp.cmp(outfile_name, filename, shallow=False):
                        # Only backup and write the source file if changes have been made (original is
                        # left in place without a backup if nothing's changed)

                        files.backup(filename)

                        shutil.move(outfile_name, filename)

                    else:
                        # Output file hasn't been used, so just delete it

                        os.unlink(outfile_name)

        except FileNotFoundError as exc:
            print(exc)
            sys.exit(1)

    else:
        cleanfile(args, sys.stdin, sys.stdout)

################################################################################

def readable():
    """Entry point"""

    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    readable()
