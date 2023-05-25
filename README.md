# Ansible Apache 2, a tool to deploy Virtual Hosts on Apache 2 with Ansible

Ansible Apache2 is a CLI that can help you to generate an Ansible Playbook to deploy multiple Virtual Hosts.

## 1. Get Started
First, you will need to install depedencies. This will need `Python3` and `Ansible`.

To install these, you will need to run those command into your terminal: 

```shell
$ sudo apt install python3 ansible
```

## 2.Usage

To use it at first, you will need clone the repo by using the following command:

```shell
$ git clone https://github.com/kirisaki-vk/ansible-apache2.git
```

You can see all available options by executing:
```shell
$ python3 generate_playbook.py --help
```

There are several options you will need to specify to generate an ansible playbook yaml file

 - **`--target` or `-t`**: Indicates your hosts name in your inventory **[Required]**
 - **`--input` or ``-i`**: Path to the file of _sites lists_* **[Required]**
 - **`--template` or `-m`**: Path to the Apache2 configuration path. Variables are `item.1` for the allocated **port** and `item.0` is the **sites name** **[Required]**
 - **`--ssk_key` or `-k`**: Path to your private ssh key **[Required]**
 - **`--output` or `-o`**: Name of the output playbook file (Default is `output.ansible.yaml`)
 - **`--user` or `-u`**: Username to connect for each hosts by ssh (Default is `root` user)
 - **`--version` or `-v`**: Display programs version

> Notes: *Sites list are a file wich contains a list of the sites to deploy separated by new line like below

```
https://www.example.com
https://www.google.com
www.github.com
https://www.openai.com
https://www.stackoverflow.com
...
...
```
> Sites name inside that list can include protocol (http:// or https://) or not, they will be treated the same 
> 
> Warning: That file doesn't support comments or nested structures (for now but IDK yet)

After running the command you can play the generated playbook to deploy them then put your index.html into each individual sites root.

> Note: sites starting with `www.` will be placed into `/var/www` and so on.