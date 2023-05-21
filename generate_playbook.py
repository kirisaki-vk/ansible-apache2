#!/usr/bin/env python3

import yaml
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
args_parser.add_argument("-u", "--user", help='''User to log in (Default is 'root')''', required=False, default="root")
args_parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

args = args_parser.parse_args()

yaml_header = "---"
yaml_data = {
    'name': 'Deploying hosts',
    'host': f'{args.target}',
    'remote_user': f'{args.user}',
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


def generate_task(list):
    port_number = 49152
    for link in list:
        port_number += 1
        path = link
        subpath = link

        splitted_link = link.split()
        yaml_data['tasks'].append({
            'name': f'Deploying {link}',
            'vars': {
                'link': link,
                'port': port_number,
                'path': path,
                'subpath': subpath
            },
            'ansible.builtin.template': {
                'src': './template/Apache2_config.template.j2',
                'dest': f'/etc/apache2/sites-available/{link}.conf'
            }
        })

generate_task(parse_list('test.txt'))

with open(args.output, 'w') as output:
    yaml.dump(yaml_data, output, sort_keys=False, explicit_start=True)