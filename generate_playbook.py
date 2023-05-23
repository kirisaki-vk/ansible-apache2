#!/usr/bin/env python3

from ruamel.yaml import YAML
import argparse
from urllib.parse import urlparse

args_parser = argparse.ArgumentParser(
    prog='ansible2apache',
    description='A simple program wich generate an Ansible playbook to deploy multiple Virtual Hosts',
    epilog='Written by Kirisaki_VK'
)

args_parser.add_argument("-t", "--target", help='''Hosts name''', required=True)
args_parser.add_argument("-i", "--input", help='''File containing the list to parse''', required=True)
args_parser.add_argument("-o", "--output", help='''Output filename (Default 'output.ansible.yaml')''', required=False,
                         default="./output.ansible.yaml")
args_parser.add_argument("-m", "--template", help='''Path to the configuration template. Variables are "port", "link", "path", "subpath"''', required=True)
args_parser.add_argument("-u", "--user", help='''User to log in (Default is 'root')''', required=False, default="root")
args_parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

args = args_parser.parse_args()

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.explicit_start = True

yaml_data = {
    'name': 'Deploying hosts',
    'host': f'{args.target}',
    'remote_user': f'{args.user}',
    'become': True,
    'tasks': [
        {
            'name': 'Check if apache is installed and in the lastest version',
            'ansible.builtin.apt': {
                'name': 'apache2',
                'status': 'lastest'
            }
        }
    ]
}


def parse_list(file):
    with open(file, 'r') as list:
        lines = list.readlines()

    return [urlparse(line.strip()).netloc for line in lines]

def generate_list(list):
    port_number = 49152
    yaml_data['tasks'].append({
        'name': 'Deploying hosts',
        'vars': {
            'links': list
        },
        'ansible.builtin.file': {
            'path': "/var/{{  link.split('.')[0] }}/{{ link.split('.')[1] }}",
            'state': 'directory',
            'mode' : '0755'
        },
        'ansible.builtin.copy': {
            'src': args.template,
            'dest': '/etc/apache2/sites-available/{{ link }}.conf',
            'owner': 'root',
            'group': 'root',
            'mode': '0644'
        },
        'ansible.builtin.file': {
            'src': '/etc/apache2/sites-available/{{ link }}.conf',
            'dest': '/etc/apache2/sites-enabled/{{ link }}.conf',
            'state': 'link'
        }
        ,
        'loop': '{{ links }}',
        'loop_control': {
            'loop_var': 'link'
        }
    })

generate_list(parse_list('test.txt'))

with open(args.output, 'w') as output:
    yaml.dump(yaml_data, output)