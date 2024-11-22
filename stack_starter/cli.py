import argparse
import os
import subprocess

def parse_sys_args():
    # Setup top level parser
    parser = argparse.ArgumentParser(description="A utility for provision machines and configure software stacks based on predefined recipes")
    parser.add_argument("-d", "--directory", help="Working directory for storing provisioning output", default="/tmp/stack_starter/")
    parser.add_argument("-r", "--recipe-path", help="Path to directory where recipies are stored", default="./../recipes")
    subparsers = parser.add_subparsers(title="CMD", description="Sub-commands", required=True)

    # Setup sub-parser for provision sub-command
    parser_provision = subparsers.add_parser("provision", description="Provision machines and networks from bare metal or cloud providers", epilog="Return an Ansible hostfile of the provisioned machines")
    parser_provision.add_argument("infra", help="Name of the infrastructure to provision or configure")
    parser_provision.add_argument("provider", help="Infrastructure provider for the machines to provision")
    parser_provision.add_argument("recipe", help="Recipe for provisioning")
    parser_provision.set_defaults(cmd="provision")

    # Setup sub-parser for configure sub-command
    parser_configure = subparsers.add_parser("configure", description="Configure software stack on a specified infrastructure")
    parser_configure.add_argument("infra", help="Name of the infrastructure to configure. Use localhost to configure the current machine.", default="localhost")
    parser_configure.add_argument("recipe", help="Recipe for configure the infrastructure")
    parser_configure.set_defaults(cmd="configure")
    
    # Parse and return arguments in Name space object
    # Example: Namespace(infra='home', directory='/tmp/stack_starter/', recipe='mac_os_host', cmd='configure')
    return parser.parse_args()

def provision(infra : str, provider : str, recipe : str):
    pass

def configure(infra : str, recipe : str, working_dir: str, recipe_path: str): 
    recipe_dir = os.path.join(recipe_path, recipe)
    infra_path = os.path.join(working_dir, infra)

    if infra == "localhost":
        os.makedirs(os.path.dirname(infra_path), exist_ok=True)
        with open(infra_path, 'w') as inventory_file:
            inventory_file.write("[local]\nlocalhost ansible_connection=local\n")
    
    if not os.path.isdir(recipe_dir):
        raise FileNotFoundError(f"Recipe directory '{recipe_dir}' does not exist.")

    if not os.path.exists(infra_path):
        raise FileNotFoundError(f"Infrastructure at '{infra_path}' does not exist.")
 
    os.chdir(recipe_dir) 
    
    ansible_command = [
        "ansible-playbook",
        "playbook.yml",
        "-i", infra_path
    ]
    
    subprocess.run(ansible_command, check=True)

def main():
    args = parse_sys_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    working_dir = os.path.abspath(args.directory) if os.path.isabs(args.directory) else os.path.join(script_dir, args.directory)
    recipe_dir = os.path.abspath(args.recipe_path) if os.path.isabs(args.recipe_path) else os.path.join(script_dir, args.recipe_path)

    if args.cmd == "provision":
        provision(args.infra, args.provider, args.recipe)
    elif args.cmd == "configure":
        configure(args.infra, args.recipe, working_dir, recipe_dir) 

    

    # print("Welcome to Stack Starter!")
    # Add your CLI logic here

if __name__ == "__main__":
    main()
