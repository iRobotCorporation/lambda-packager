"""Manipulation of the output of code upload

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
import json
import argparse

from .parameters import BUILD_DIR, get_function_build_dir

UPLOAD_CONFIG_FILE_NAME = 'upload_config'
MERGED_UPLOAD_CONFIG_FILE = os.path.join(BUILD_DIR, UPLOAD_CONFIG_FILE_NAME)

def function_upload_config_file(function_name):
    os.path.join(get_function_build_dir(function_name), UPLOAD_CONFIG_FILE_NAME)

def load_upload_config(function_name):
    with open(function_upload_config_file(function_name), 'r') as fp:
        return json.load(fp)

def load_and_merge_upload_configs(function_names):
    upload_config = {}
    for function_name in function_names:
        upload_config.update(load_upload_config(function_name))
    return upload_config

def load_merged_upload_config():
    with open(MERGED_UPLOAD_CONFIG_FILE, 'r') as fp:
        return json.load(fp)

def print_upload_config_main(args, other_args):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--input-config', type=json.loads)
    parser.add_argument('--pretty', action='store_true')
    
    print_args = parser.parse_args(args=other_args)
    
    if print_args.input_config:
        upload_config = load_and_merge_upload_configs(six.iterkeys(print_args.input_config))
    else:
        upload_config = load_merged_upload_config()
    
    kwargs = {}
    
    if print_args.pretty:
        kwargs['indent'] = 2
    
    json.dump(upload_config, **kwargs)
    return 0

def merge_upload_config_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', nargs=2)
    parser.add_argument('-o')
    
    args = parser.parse_args()
    
    merged_config = {}
    for logical_id, upload_config_path in args.i:
        with open(upload_config_path, 'r') as fp:
            merged_config[logical_id] = json.load(fp)
    with open(args.o, 'w'):
        json.dumps(merged_config)
    return 0

def get_make_args(action, args, other_args):
    make_args = [
        'MERGED_UPLOAD_CONFIG_FILE={}'.format(MERGED_UPLOAD_CONFIG_FILE),
        'UPLOAD_CONFIG_FILE_NAME={}'.format(UPLOAD_CONFIG_FILE_NAME),
    ]
    return make_args
