#! /usr/bin/env python3

################################################################################
""" Simple AWS module - provides an abstraction layer on top of the boto3 client
    for simple operations such as reading/writing S3 buckets, sending emails
    etc.

    Currently this is a random collection of functions extracted from the S3
    bucket ACL checking code but it is hoped it will evolve over time into
    something more comprehensive.

    Author: John Skilleter
"""
################################################################################

# System modules

import sys
import logging
import json

# AWS modules

import boto3
import botocore

################################################################################

class GenericAWS:
    """ Class providing generic S3 functionality from which the
        other S3 classes are derived """

    ################################################################################

    def __init__(self, service, session=None, profile=None, createresource=True, createclient=True, region=None):
        """ Initialisation - just create a client handle, optionally using
            the specified profile """

        if session:
            self.session = session
        elif profile:
            self.session = boto3.session.Session(profile_name=profile)
        else:
            self.session = boto3

        args = {}
        if region:
            args['region_name'] = region

        if createresource:
            self.resource = self.session.resource(service, **args)

        if createclient:
            self.client = self.session.client(service, **args)

        self.log = logging.getLogger('%s:%s' % (__name__, service))

    ################################################################################

    def set_log_level(self, level):
        """ Set logging for the module """

        self.log.setLevel(level)

################################################################################

class SES(GenericAWS):
    """ Class for AWS Simple Email Service """

    ################################################################################

    def __init__(self, session=None, profile=None):
        """ Initialisation """

        super().__init__('ses', session, profile, createresource=False)

    ################################################################################

    def send(self, sender, recipient, subject, body):
        """ Send an email """

        destination = \
            {
                'ToAddresses': [recipient]
            }

        message = \
            {
                'Subject':
                {
                    'Data': subject
                },
                'Body':
                {
                    'Text':
                    {
                        'Data': body
                    }
                }
            }

        # Attempt to send the email - just report the error and quit on failure

        try:
            self.log.info('Sending email from %s to %s', sender, recipient)

            self.client.send_email(Source=sender,
                                   Destination=destination,
                                   Message=message)

        except (botocore.exceptions.EndpointConnectionError,
                self.client.exceptions.MessageRejected) as err:
            print('')
            print('Error sending email: %sn' % err)
            print('    Sender:    %s' % sender)
            print('    Recipient: %s' % recipient)
            print('    Subject:   %s' % subject)
            print('    Body:')

            for txt in body.split('\n'):
                print('        %s' % txt)

            print('')

            sys.exit(1)

################################################################################

class S3Bucket(GenericAWS):
    """ Class providing access to S3 buckets """

    ################################################################################

    def __init__(self, session=None, profile=None):
        """ Initialisation - just create a client handle, optionally using
            the specified profile """

        super().__init__('s3', session, profile)

    ################################################################################

    def read(self, bucket, key):
        """ Read the specified data from the specified bucket.
            Returns the data, or raises a boto3 exception on error. """

        self.log.info('Get object from key %s in bucket %s', key, bucket)

        response = self.client.get_object(Bucket=bucket, Key=key)

        self.log.debug('Get object: %s', response)

        return response['Body'].read()

    ################################################################################

    def write(self, bucket, key, data):
        """ Write data into the specified key of the specified bucket
            Raises a boto3 exception on error. """

        self.log.info('Writing %d bytes of data to key %s in bucket %s', len(data), key, bucket)

        self.client.put_object(Bucket=bucket, Key=key, Body=data)

    ################################################################################

    def get_tags(self, bucket):
        """ Read the tags from a bucket. Returns a dictionary of tags, which will be
            empty if the bucket has no tags. """

        self.log.info('Reading tags from bucket %s', bucket)

        try:
            tags = self.client.get_bucket_tagging(Bucket=bucket)['TagSet']

        except botocore.exceptions.ClientError as err:
            # Any exception except NoSuchTagSet gets raised.
            # NoSuchTagSet simply means that the bucket has no tags
            # and isn't really an error, as such, so we just return
            # an empty dictionary.

            if err.response['Error']['Code'] != 'NoSuchTagSet':
                self.log.error('Error reading tags for bucket %s: %s', bucket, err.response['Error']['Code'])
                raise

            tags = {}

        self.log.info('Tags: %s', tags)

        return tags

    ################################################################################

    def get_location(self, bucket):
        """ Return the location of a bucket - note that the Boto3 returns the location
            set to none, rather than us-east-1 if you query a bucket located in that
            region. """

        try:
            location = self.client.get_bucket_location(Bucket=bucket)['LocationConstraint']
        except botocore.exceptions.ClientError as err:
            self.log.info('Error getting location of bucket %s: %s', bucket, err.response['Error']['Code'])
            raise

        if not location:
            location = 'us-east-1'

        return location

    ################################################################################

    def get_acl(self, bucket):
        """ Return the bucket ACLs """

        try:
            return self.client.get_bucket_acl(Bucket=bucket)['Grants']
        except botocore.exceptions.ClientError as err:
            self.log.error('Error getting ACL for bucket %s: %s', bucket, err.response['Error']['Code'])
            raise

    ################################################################################

    def get_policy(self, bucket):
        """ Return bucket policy information as a list of policy dictionaries
            Returns an empty list if the bucket has no policies (similar to
            get_tags() above). """

        try:
            policy_data = self.client.get_bucket_policy(Bucket=bucket)

        except botocore.exceptions.ClientError as err:
            # Any exception which *isn't* a no-policy exception gets raised
            # to the caller, the no-policy one causes the function to return
            # an empty policy list.

            if err.response['Error']['Code'] != 'NoSuchBucketPolicy':
                self.log.error('Error reading policy for bucket %s: %s', bucket, err.response['Error']['Code'])
                raise

            return []

        return json.loads(policy_data['Policy'])

    ################################################################################

    def get_buckets(self):
        """ Return a list of all the available buckets """

        return [bucket.name for bucket in self.resource.buckets.all()]

    ################################################################################

    def get_website(self, bucket):
        """ Return the web site configuration for the bucket, or None if the bucket
            is not configured for hosting """

        try:
            web = self.client.get_bucket_website(Bucket=bucket)

        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] != 'NoSuchWebsiteConfiguration':
                print('>>>%s' % err.response)
                raise

            web = None

        return web

    ################################################################################

    def get_objects(self, bucket, max_objects=None):
        """ Yield a list of the details of the objects in a bucket, stopping after
            returning max_objects (if specified). """

        paginator = self.client.get_paginator('list_objects_v2')

        pagesize = min(25, max_objects) if max_objects else 25

        objects = paginator.paginate(Bucket=bucket, PaginationConfig={'PageSize': pagesize})

        count = 0

        for data in objects:
            if 'Contents' in data:
                for obj in data['Contents']:

                    if max_objects:
                        count += 1
                        if count > max_objects:
                            break

                    yield obj

    ################################################################################

    def get_object_acl(self, bucket, obj):
        """ Return the ACL data for an object in a bucket """

        try:
            return self.client.get_object_acl(Bucket=bucket, Key=obj)['Grants']
        except botocore.exceptions.ClientError as err:
            self.log.error('Error getting ACL for object %s in bucket %s: %s', obj, bucket, err.response['Error']['Code'])
            raise

    ################################################################################

    def get_lifecycle(self, bucket):
        """ Return the bucket lifecycle data """

        try:
            lifecycle = self.client.get_bucket_lifecycle_configuration(Bucket=bucket)
        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                lifecycle = None
            else:
                raise

        return lifecycle

################################################################################

class STS(GenericAWS):
    """ Class providing access to STS functionality """

    def __init__(self, session=None, profile=None):
        """ Initialise the STS client (there is no STS resource in boto3) """

        super().__init__('sts', session, profile, createresource=False)

    ################################################################################

    def account(self):
        """ Return the name of the current AWS account """

        return self.client.get_caller_identity()['Account']

################################################################################

class IAM(GenericAWS):
    """ Class providing access to IAM """

    def __init__(self, session=None, profile=None):
        """ Initialise the IAM client/resource """

        super().__init__('iam', session, profile, createresource=False)

    def role_exists(self, role):
        """ Return True if the role exists """

        try:
            self.client.get_role(RoleName=role)
        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] != 'NoSuchEntity':
                raise

            return False
        else:
            return True

    def create_role(self, role, description, policy):
        """ Create a new role """

        response = self.client.create_role(RoleName=role, Description=description, AssumeRolePolicyDocument=policy)

        return response

    def put_role_policy(self, role, policy_name, policy):
        """ Update the policy in an existing role """

        response = self.client.put_role_policy(RoleName=role, PolicyName=policy_name, PolicyDocument=policy)

        return response

    def get_role_policy(self, role, policy_name):
        """ Read the policy in an existing role """

        response = self.client.get_role_policy(RoleName=role, PolicyName=policy_name)

        return response

################################################################################

class Events(GenericAWS):
    """ Class providing access to CloudWatch Events """

    def __init__(self, session=None, profile=None):
        """ Initialise the CloudWatch Events client/resource """

        super().__init__('events', session, profile, createresource=False)

    def put_rule(self, name, schedule):
        """ Create or update the specified rule """

        self.client.put_rule(Name=name, ScheduleExpression=schedule)

    def put_target(self, name, targets):
        """ Add the specified target(s) to the specified rule, or update
            existing targets """

        self.client.put_targets(Rule=name, Targets=targets)

################################################################################

DEFAULT_LAMBDA_TIMEOUT = 3
DEFAULT_LAMBDA_MEMORY = 128
DEFAULT_LAMBDA_HANDLER = 'main.main'
DEFAULT_LAMBDA_RUNTIME = 'python3.6'

class Lambda(GenericAWS):
    """ Class providing access to Lambda functions """

    def __init__(self, session=None, profile=None, region=None):
        """ Initialise the Lambda client/resource """

        super().__init__('lambda', session, profile, createresource=False, region=region)

    def exists(self, name):
        """ Return True if the specified Lambda function exists """

        try:
            self.client.get_function(FunctionName=name)
        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] != 'ResourceNotFoundException':
                raise
            return False
        else:
            return True

    def update_function(self, name, zipfile):
        """ Update the specified Lambda function given a zip file """

        with open(zipfile, 'rb') as zipper:
            zipdata = zipper.read()

        response = self.client.update_function_code(FunctionName=name, ZipFile=zipdata)

        return response

    def update_function_configuration(self, name,
                                      handler=None,
                                      environment=None):
        """ Update the handler associated with a Lambda fucntion """

        update_args = {}
        update_args['FunctionName'] = name

        if handler:
            update_args['Handler'] = handler

        if environment:
            update_args['Environment'] = {'Variables': environment}

        self.client.update_function_configuration(**update_args)

    def create_function(self, name, role, description, zipfile,
                        runtime=DEFAULT_LAMBDA_RUNTIME,
                        handler=DEFAULT_LAMBDA_HANDLER,
                        timeout=DEFAULT_LAMBDA_TIMEOUT,
                        memory=DEFAULT_LAMBDA_MEMORY):
        """ Create the specified Lambda function given a zip file"""

        with open(zipfile, 'rb') as zipper:
            zipdata = zipper.read()

        response = self.client.create_function(FunctionName=name,
                                               Runtime=runtime,
                                               Role=role,
                                               Handler=handler,
                                               Code={'ZipFile': zipdata},
                                               Description=description,
                                               Timeout=timeout,
                                               MemorySize=memory)

        return response

################################################################################

def get_session(profile_name=None):
    """ Wrapper for boto3.session.Session """

    return boto3.session.Session(profile_name=profile_name)

################################################################################

def set_stream_logger(name='botocore', level=10, format_string=None):
    """ Wrapper for boto3.set_stream_logger """

    return boto3.set_stream_logger(name=name, level=level, format_string=format_string)

################################################################################

def set_default_region(region):
    """ Set the default region for the module """

    boto3.setup_default_session(region_name=region)

################################################################################

def get_regions(servicename):
    """ Generate a list of regions where a service is supported """

    return boto3.session.Session().get_available_regions(servicename)

################################################################################

def get_resources():
    """ Devious method of getting the list of clients supported by boto3
        Note that I'm somewhat embarrassed by this, but can't find a better
        way of doing it! """

    try:
        boto3.resource('XXX-NOT-A-RESOURCE-XXX')
    except boto3.exceptions.ResourceNotExistsError as err:
        return str(err).replace('   - ', '').split('\n')[2:-1]

################################################################################

def get_clients():
    """ Similarly devious way of getting the list of supported clients.
        This is equally as yukky as the get_resources() function. """

    try:
        boto3.client('XXX-NOT-A-CLIENT-XXX')
    except botocore.exceptions.UnknownServiceError as err:
        return repr(err)[:-3].split(': ')[2].split(', ')

################################################################################

def test_function():
    """ Module test function """

    # Test STS

    sts_client = STS()

    print('Current account: %s' % sts_client.account())

    # TODO: Test SES
    # TODO: Test S3
    # TODO: Test IAM
    # TODO: Test Cloudwatch Events
    # TODO: Test Lambda
    # TODO: Test set_default_region(), get_session(), get_resources(), get_regions(), get_clients()

################################################################################
# Test code

if __name__ == '__main__':
    test_function()
