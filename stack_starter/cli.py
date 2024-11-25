import argparse
import os
import subprocess
import yaml
from typing import List, Tuple
from typing_extensions import Dict

default_recipe_dirs = [
    "./..recipes",
    "/tmp/stack_starter/recipes"
]

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
        "-i", infra_path,
        "-vv",
        # "--ask-become-pass"
    ]
    
    subprocess.run(ansible_command, check=True)

def prepare_working_dir(working_dir : str): 
    # Create directory structure
    # Create empty localhost file if it does not exist
    pass

def load_recipes(recipe_dirs : List[str]) -> Tuple[Dict[str, str], Dict[str, str]]:
    provision_recipes = {}
    configure_recipes = {}

    for recipe_dir in recipe_dirs:
        for root, _, files in os.walk(recipe_dir):
            for file in files:
                if file == "manifest.yaml":
                    manifest_path = os.path.join(root, file)
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = yaml.safe_load(f)
                            recipe_name = manifest.get('name')
                            recipe_type = manifest.get('recipe_type')
                            print(f"detected {file}")
                            # print(f"manifest name: {recipe_type}")
                            
                            if recipe_type == 'provision':
                                provision_recipes[recipe_name] = manifest
                            elif recipe_type == 'configure':
                                configure_recipes[recipe_name] = manifest
                    except yaml.YAMLError as e:
                        print(f"Error loading YAML file {manifest_path}: {e}")
    return provision_recipes, configure_recipes

def prepare_dir_list(dir : str, default_dirs : List[str] = []) -> List[str]:
    valid_dirs = []
    combined_dirs = [dir] + default_dirs
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for dir in combined_dirs:
        if os.path.isdir(dir):
            if os.path.isabs(dir):
                valid_dirs.append(dir)
            else:
                valid_dirs.append(os.path.abspath(os.path.join(script_dir, dir)))

    return valid_dirs


def main():
    # Parse system args
    args = parse_sys_args()
    # Setup paths, prepare working directory, and load recipes
    script_dir = os.path.dirname(os.path.abspath(__file__))    
    working_dir = os.path.abspath(args.directory) if os.path.isabs(args.directory) else os.path.join(script_dir, args.directory)
    recipe_dir = os.path.abspath(args.recipe_path) if os.path.isabs(args.recipe_path) else os.path.join(script_dir, args.recipe_path)
    recipe_dirs = prepare_dir_list(args.recipe_path, default_recipe_dirs)
    configure_recipe_dir = os.path.join(recipe_dir, "configure")
    provision_recipe_dir = os.path.join(recipe_dir, "provision")

    # Prepare working directory
    prepare_working_dir(working_dir)
    # Detect and load all the recipes
    provision_recipes, configure_recipes = load_recipes(recipe_dirs)

    if args.cmd == "provision":
        # Throw if the required provision_recipe is not available
        provision(args.infra, args.provider, args.recipe)
    elif args.cmd == "configure":
        # Throw if the required configure recipe is not available
        if args.recipe not in configure_recipes:
            raise ValueError(f"Configure recipe '{args.recipe}' does not exist.")
        configure(args.infra, args.recipe, working_dir, configure_recipe_dir) 

    

    # print("Welcome to Stack Starter!")
    # Add your CLI logic here

if __name__ == "__main__":
    main()
