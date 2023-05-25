#!/usr/bin/env python3

from ruamel.yaml import YAML
import argparse
from urllib.parse import urlparse
from io import StringIO

args_parser = argparse.ArgumentParser(
    prog='ansible2apache',
    description='A simple CLI wich generate an Ansible playbook to deploy multiple Virtual Hosts',
    epilog='Written by Kirisaki_VK'
)

args_parser.add_argument("-t", "--target", help='''Hosts name''', required=True)
args_parser.add_argument("-i", "--input", help='''File containing the list to parse''', required=True)
args_parser.add_argument("-o", "--output", help='''Output filename (Default 'output.ansible.yaml')''', required=False,
                         default="./output.ansible.yaml")
args_parser.add_argument("-k", "--ssh_key", help="Path to the private ssh key file",required=True)
args_parser.add_argument("-m", "--template", help='''Path to the configuration template. Variables are "item.0": link, "item.1": port''', required=True)
args_parser.add_argument("-u", "--user", help='''User to log in (Default is 'root')''', required=False, default="root")
args_parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

args = args_parser.parse_args()

yaml = YAML(typ=['rt', 'string'])
yaml.indent(mapping=2, sequence=4, offset=2)

def parse_list(file):
    with open(file, 'r') as list:
        lines = list.readlines()
        ret = []

        for line in lines:
            if not urlparse(line.strip()).netloc:
               ret.append(urlparse(line.strip()).path)
            else : ret.append(urlparse(line.strip()).netloc)

    return ret


lists = parse_list(args.input)
port_number = 49152

yaml_data = [{
    'name': 'Deploying hosts',
    'hosts': f'{args.target}',
    'remote_user': f'{args.user}',
    'become': True,
    'vars': {
        'ansible_ssh_private_key_file': f'{args.ssh_key}',
        'links': lists,
        'port': [ host for host in range(port_number, port_number + len(lists)) ]
    },
    'tasks': [
        {
            'name': 'Getting package facts',
            'ansible.builtin.package_facts': {
                'manager': 'auto'
            }
        },
        {
            'name': 'Stop execution if ansible is not present',
            'ansible.builtin.meta': {
                'end_play': 'true'
            },
            'when': "'apache2' not in ansible_facts.packages"
        }
    ]
}]

def generate_list():
    body = [{
        'name': 'Generating sites root',
        'ansible.legacy.file': {
            'path': "/var/{{  link.split('.')[0] }}/{{ link.split('.')[1] }}",
            'state': 'directory',
            'mode' : '0755'
        },
        'loop': '{{ links }}',
        'loop_control': {
            'loop_var': 'link'
        }
    },
    {
        'name': 'Copying files configuration',
        'ansible.builtin.template': {
            'src': args.template,
            'dest': '/etc/apache2/sites-available/{{ item.0 }}.conf',
            'owner': 'root',
            'group': 'root',
            'mode': '0644'
        },
        'with_together': [
            '{{ links }}',
            '{{ port }}'
        ]
    },
    {
        'name': 'Enabling sites',
        'ansible.legacy.file': {
            'src': '/etc/apache2/sites-available/{{ link }}.conf',
            'dest': '/etc/apache2/sites-enabled/{{ link }}.conf',
            'state': 'link'
        },
        'loop': '{{ links }}',
        'loop_control': {
            'loop_var': 'link'
        }
    }]

    for items in body:
        yaml_data[0]['tasks'].append(items)

generate_list()

yaml_data_dump = StringIO()
yaml.dump(yaml_data, yaml_data_dump)
yaml_data_dump.seek(0)
yaml_string = yaml_data_dump.read().split('\n')

yaml_corrected = [ lines[2:] for lines in yaml_string]
yaml_corrected.insert(0, '---')
yaml_corrected = '\n'.join(yaml_corrected)

with open(args.output, 'w') as output:
    output.write(yaml_corrected)
