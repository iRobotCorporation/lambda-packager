"""Input configuration functions

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

import six
import argparse
import json
import os.path

import yaml

try:
    import cfn_yaml_tags
    cfn_yaml_tags.mark_safe()
    json_encoder = cfn_yaml_tags.JSONFromYAMLEncoder()
except:
    json_encoder = json.JSONEncoder()

def config_from_template(template):
    output = {}
    for resource_name, resource in six.iteritems(template.get('Resources', {})):
        properties = resource.get('Properties', {})
        if 'CodeUri' in properties:
            entry = {
                'CodeUri': properties['CodeUri'],
            }
            if resource.get('Type') == 'AWS::Serverless::Function' and 'FunctionName' in properties:
                entry['FunctionName'] = properties['FunctionName']
            output[resource_name] = entry
    return output

def load_config_from_template_file(template):
    if isinstance(template, six.string_types):
        with open(template, 'r') as fp:
            template = yaml.safe_load(fp)
    else:
        template = yaml.safe_load(template)
    return config_from_template(template)

def get_config(
        config=None,
        template=None,
        code_uri=None,
        function_name=None):
    if config:
        return config
    if template:
        return load_config_from_template_file(template)
    if not code_uri:
        raise RuntimeError("No config defined")
    entry = {
        'CodeUri': code_uri,
    }
    if function_name:
        entry['FunctionName'] = function_name
    config = {
        os.path.basename(code_uri): entry,
    }
    return config

def print_config(config):
    six.print_('{:<24} {:<24} {:<24}'.format('LogicalId', 'FunctionName', 'CodeUri'))
    for logical_id, entry in six.iteritems(config):
        code_uri = entry['CodeUri']
        function_name = entry.get('FunctionName', '')
        six.print_('{:<24} {:<24} {:<24}'.format(logical_id, function_name, code_uri))

def add_config_args(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--config', type=json.loads)
    group.add_argument('--template', type=argparse.FileType('r'))
    manual_config_group = group.add_argument_group()
    manual_config_group.add_argument('--code-uri')
    manual_config_group.add_argument('--function-name')

def get_config_from_args(args):
    kwargs = {}
    for name in ['config', 'template', 'code_uri', 'function_name']:
        kwargs[name] = getattr(args, name)
    return get_config(**kwargs)

# def config_from_template_main(args=None):
#     import file_transformer
#     def processor(input, args):
#         return config_from_template(input)
#     def loader(input_stream, args):
#         return yaml.safe_load(input_stream)
#     def dumper(output, output_stream, args):
#         output_stream.write(json_encoder.encode(output))
#     file_transformer.main(processor, loader, dumper, args=args)

def print_config_main(args, other_args):
    print_config(get_config_from_args(args))
    return 0

def get_make_args(action, args, other_args):
    make_args = []
    if action == 'clean':
        make_args.append('CONFIG=')
    else:
        make_args.append('CONFIG={}'.format(json.dumps(get_config_from_args(args))))
    return make_args
