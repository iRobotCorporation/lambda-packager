"""Input parameters

Copyright 2018 iRobot Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import absolute_import, print_function

import os.path
import six
import sys

BUILD_DIR = './.build'
BUCKET_PATTERN = '{bucket_prefix}-{account}-{region}'

def get_function_build_dir(function_name):
    return os.path.join(BUILD_DIR, function_name)

def add_parameter_args(parser):
    bucket_group = parser.add_mutually_exclusive_group()
    bucket_group.add_argument('--bucket')
    bucket_group.add_argument('--bucket-prefix')
    
    parser.add_argument('--aws-args')

def get_make_args(action, args, other_args):
    make_args = [
        'BUILD_DIR={}'.format(BUILD_DIR),
        'PYTHON_VERSION={0}.{1}'.format(*sys.version_info)
    ]
    if args.bucket:
        make_args.append('BUCKET={}'.format(args.bucket))
    elif args.bucket_prefix:
        import boto3
        session = boto3.Session()
        region = session.region_name
        account = session.client('sts').get_caller_identity()['Account']
        bucket = BUCKET_PATTERN.format(bucket_prefix=args.bucket_prefix, account=account, region=region)
        make_args.append('BUCKET={}'.format(bucket))
    
    if args.aws_args:
        make_args.append('AWS_ARGS={}'.format(args.aws_args))
    
    return make_args