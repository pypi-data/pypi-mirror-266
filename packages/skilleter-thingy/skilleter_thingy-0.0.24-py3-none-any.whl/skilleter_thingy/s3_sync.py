#!/usr/bin/env python3

"""Selectively synchronise an S3 bucket to a local destination.
   Similar to the aws s3 sync CLI command, but faster, has better
   options to filter files, only downloads from S3 to local and
   doesn't support the huge range of command line options."""

import os
import argparse
import sys
import fnmatch
import datetime
import threading
import queue

from pathlib import Path

import boto3

from botocore.exceptions import ClientError

################################################################################

# Number of download threads to run - doing the downloads in threads is about
# six times faster than doing so sequentially.

NUM_THREADS = 12

# Translate our environment names to AWS ARNs

AWS_ACCOUNT_ARNS = {
    'prod': 'arn:aws:iam::459580378985:role/ERSReadOnlyRole',
    'test': 'arn:aws:iam::094438481629:role/ERSReadOnlyRole',
    'dev': 'arn:aws:iam::402653103803:role/ERSReadOnlyRole',
    'mgmt': 'arn:aws:iam::125943076446:role/ERSReadOnlyRole',
    'audit': 'arn:aws:iam::229627323276:role/ERSReadOnlyRole',
}

################################################################################

def error(msg, status=1):
    """Report an error message and exit"""

    print(f'ERROR: {msg}')
    sys.exit(status)

################################################################################

def verbose(args, msg):
    """Report a message in verbose mode"""

    if not args or args.verbose:
        print(msg)

################################################################################

def splitlist(lists, deliminator):
    """Create a list from a list of deliminated strings"""

    result = []

    for item in lists or []:
        result += item.split(deliminator)

    return result

################################################################################

def configure():
    """Parse the command line"""

    parser = argparse.ArgumentParser(description='Selectively sync an S3 bucket to a local directory')

    parser.add_argument('--verbose', '-v', action='store_true', help='Report verbose results (includes number of commits between branch and parent)')

    parser.add_argument('--profile', '-p', action='store', help='Specify the AWS profile')

    parser.add_argument('--include', '-i', action='append', help='Comma-separated list of wildcards to sync - if specified, only files matching one or more of these are synced')
    parser.add_argument('--exclude', '-x', action='append', help='Comma-separated list of wildcards NOT to sync - if specified, only files NOT matching any of these are synced')

    parser.add_argument('--include-type', '-I', action='append',
                        help='Comma-separated list of file types to sync - if specified, only files matching one or more of these are synced')
    parser.add_argument('--exclude-type', '-X', action='append',
                        help='Comma-separated list of file types NOT to sync - if specified, only files NOT matching any of these are synced')

    # TODO: parser.add_argument('--delete', '-d', action='store_true', help='Delete local files that don\'t exist in the bucket')
    parser.add_argument('--force', '-f', action='store_true', help='Always overwrite locals files (by default files are only overwritten if they are older or a different size)')

    parser.add_argument('--max-objects', '-m', action='store', type=int, help='Limit the number of objects to download')
    parser.add_argument('--threads', '-t', action='store', type=int, default=NUM_THREADS, help='Number of parallel threads to run')
    parser.add_argument('source', action='store', nargs=1, type=str, help='Name of the S3 bucket, optionally including path within the bucket')
    parser.add_argument('destination', action='store', nargs=1, type=str, help='Name of the local directory to sync into')

    args = parser.parse_args()

    # Convert the arguments to single items, but 1-entry lists

    args.source = args.source[0]
    args.destination = args.destination[0]

    # Convert the include/exclude parameters to lists

    args.include = splitlist(args.include, ',')
    args.exclude = splitlist(args.exclude, ',')

    args.include_type = splitlist(args.include_type, ',')
    args.exclude_type = splitlist(args.exclude_type, ',')

    return args

################################################################################

def get_client(args):
    """Create an S3 client for the specified profile"""

    if args.profile:
        profile = args.profile.split('-')[0]
    else:
        try:
            profile = os.environ['AWS_PROFILE']
        except KeyError:
            error('The AWS profile must be specified via the AWS_PROFILE environment variable or the --profile command line option')

    try:
        arn = AWS_ACCOUNT_ARNS[profile]
    except KeyError:
        error(f'Invalid AWS profile "{profile}"')

    sts_connection = boto3.client("sts")

    try:
        acct_b = sts_connection.assume_role(RoleArn=arn, RoleSessionName='s3-selective-sync')
    except ClientError as exc:
        error(f'{exc.response["Error"]["Message"]}')

    access_key = acct_b["Credentials"]["AccessKeyId"]
    secret_key = acct_b["Credentials"]["SecretAccessKey"]
    session_token = acct_b["Credentials"]["SessionToken"]

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token)

    return session.client('s3')

################################################################################

def download_filter(args, s3_client, s3_bucket, s3_object):
    """Decide whether to download an object from S3
       Returns True if the object should be downloaded, or False if it should be skipped."""

    # Ignore directories

    if s3_object['Key'][-1] == '/':
        verbose(args, f'{s3_object["Key"]} is a prefix, so will be skipped')
        return False

    # Handle the object as a Path for simpicity

    object_path = Path(s3_object['Key'])

    # Filter according to wildcard

    if args.include:
        for wildcard in args.include:
            if '/' in wildcard:
                if fnmatch.fnmatch(s3_object['Key'], wildcard):
                    break
            elif fnmatch.fnmatch(object_path.name, wildcard):
                break
        else:
            verbose(args, f'"{s3_object["Key"]}" does not match any include wildcards, so will be skipped')
            return False

    if args.exclude:
        for wildcard in args.exclude:
            if '/' in wildcard:
                if fnmatch.fnmatch(s3_object['Key'], wildcard):
                    verbose(args, f'"{s3_object["Key"]}" matches one or more exclude wildcards, so will be skipped')
            elif fnmatch.fnmatch(object_path.name, wildcard):
                verbose(args, f'"{s3_object["Key"]}" matches one or more exclude wildcards, so will be skipped')
                return False

    # Filter according to content type

    if args.include_type or args.exclude_type:
        object_type = s3_client.head_object(Bucket=s3_bucket, Key=s3_object["Key"])['ContentType']

        if args.include_type:
            for include_type in args.include_type:
                if object_type == include_type:
                    break
            else:
                verbose(args, f'"{s3_object["Key"]}" is of type "{object_type}" which does not match any entries in the the type include list, so will be skipped')
                return False

        if args.exclude_type:
            for exclude_type in args.exclude_type:
                if object_type == exclude_type:
                    verbose(args, f'"{s3_object["Key"]}" is of type "{object_type}" which matches one of the entries in the type exclude list, so will be skipped')
                    return False

    # Unless we are in force-download mode, check if the destination file already exists and see if it needs to be overwritten

    if not args.force:
        dest_file = args.destination / object_path

        if dest_file.exists():
            # Overwrite if destination is older or a different size

            dest_stat = dest_file.stat()
            dest_timestamp = datetime.datetime.fromtimestamp(dest_stat.st_mtime, tz=datetime.timezone.utc)

            if dest_timestamp >= s3_object['LastModified']:
                verbose(args, f'Destination file already exists and is same age or newer, so "{s3_object["Key"]}" will be skipped')
                return False

    return True

################################################################################

def download(args, s3_client, mkdir_lock, bucket, s3_object):
    """Attempt to download an object from S3 to an equivalent local location"""

    local_path = Path(args.destination) / s3_object['Key']

    with mkdir_lock:
        if local_path.parent.exists():
            if not local_path.parent.is_dir():
                error(f'Unable to download "{s3_object["Key"]}" as the destination path is not a directory')
        else:
            local_path.parent.mkdir(parents=True)

    # Download the object and the set the file timestamp to the same as the object

    object_timestamp = s3_object['LastModified'].timestamp()
    s3_client.download_file(bucket, s3_object['Key'], local_path)
    os.utime(local_path, (object_timestamp, object_timestamp))

################################################################################

def downloader(args, s3_client, mkdir_lock, bucket, object_queue, error_queue, sem_counter, real_thread=True):
    """Download thread"""

    finished = False
    while not finished:
        # Get the next object to download (waiting for one to be added to the queue)

        s3_object = object_queue.get()

        # If it is a candidate for downloading (meetings the criteria specified on the command
        # line and, unless force-downloading, hasn't already been downloaded) then attempt to
        # download it.

        # If the semaphore is being used to limit the number of downloads, attempt to acquire it
        # If we couldn't, then we've reached the download limit so we'll finish.

        if download_filter(args, s3_client, bucket, s3_object):

            if not sem_counter or sem_counter.acquire(blocking=False):
                print(f'Downloading "{s3_object["Key"]}"')
                try:
                    download(args, s3_client, mkdir_lock, bucket, s3_object)
                except ClientError as exc:
                    error_queue.put(f'Failed to download "{s3_object["Key"]}" - {exc.response["Error"]["Message"]}')

                    if sem_counter:
                        sem_counter.release()
                else:
                    print(f'       Done "{s3_object["Key"]}"')

            else:
                finished = True

        # Indicate the queued item has been consumed

        object_queue.task_done()

    # If we were using a download semaphore then drain the queue (this will happen in all
    # threads and will never terminate, but we're running as a daemon so it doesn't matter too much).

    if sem_counter and real_thread:
        while True:
            object_queue.get()
            object_queue.task_done()

################################################################################

def thread_exception_handler(args):
    """Brute-force thread exception handler"""

    _ = args
    sys.exit(1)

################################################################################

def main():
    """Entry point"""

    args = configure()

    s3_client = get_client(args)

    bucket = args.source

    # Remove the 's3://' prefix, if present so that we can split bucket and folder
    # if specified

    if bucket.startswith('s3://'):
        bucket = bucket[5:]

    if '/' in bucket:
        bucket, prefix = bucket.split('/', 1)
    else:
        prefix = ''

    # Semaphore to protect download counter

    sem_counter = threading.Semaphore(value=args.max_objects) if args.max_objects else None

    # Create the download queue and the worker threads

    object_queue = queue.Queue()

    # Create the queue for reporting errors back from the threads

    error_queue = queue.Queue()

    # Lock to prevent race conditions around directory creation

    mkdir_lock = threading.Lock()

    if args.threads > 1:
        # Create threads

        threading.excepthook = thread_exception_handler

        for _ in range(NUM_THREADS):
            thread = threading.Thread(target=downloader, daemon=True, args=(args, s3_client, mkdir_lock, bucket, object_queue, error_queue, sem_counter))
            thread.start()

    # Read all the objects in the bucket and queue them for consideration by the download workers

    for page in s3_client.get_paginator('list_objects_v2').paginate(Bucket=bucket, Prefix=prefix):
        for s3_object in page['Contents']:
            object_queue.put(s3_object)

    print('Finished queuing objects')

    if args.threads > 1:
        # Wait for the queues to drain

        object_queue.join()
    else:
        downloader(args, s3_client, mkdir_lock, bucket, object_queue, error_queue, sem_counter, real_thread=False)

    # Report any errors:

    if not error_queue.empty():
        sys.stderr.write('\nErrors were encountered downloading some of the objects:\n\n\n')

        while not error_queue.empty():
            error_msg = error_queue.get()
            sys.stderr.write(f'{error_msg}\n')
            error_queue.task_done()

################################################################################

def s3_sync():
    """Entry point"""

    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    s3_sync()
