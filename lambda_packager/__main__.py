"""Main scripts

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

import subprocess
import pkg_resources
import sys
import argparse
import six

from . import parameters, input_config, upload_config

def run_make(action, args, other_args):
    with pkg_resources.resource_stream(__name__, 'Makefile') as fp:
        make_args = []
        make_args += parameters.get_make_args(action, args, other_args)
        make_args += input_config.get_make_args(action, args, other_args)
        make_args += upload_config.get_make_args(action, args, other_args)
        return subprocess.call(['make', '-f', '-'] + make_args + [action], stdin=fp)

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('action', choices=['print_config', 'build', 'upload', 'print_upload_config', 'clean'])
    parameters.add_parameter_args(parser)
    input_config.add_config_args(parser)
    
    args, other_args = parser.parse_known_args()
    
    if args.action == 'print_config':
        sys.exit(input_config.print_config_main(args, other_args))
    elif args.action == 'print_upload_config':
        sys.exit(upload_config.print_upload_config_main(args, other_args))
    else:
        sys.exit(run_make(args.action, args, other_args))

if __name__ == '__main__':
    main()