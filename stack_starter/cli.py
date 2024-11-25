import argparse
import os
import subprocess
import yaml
from typing import List, Tuple
from typing_extensions import Dict
from runners import ansible_runner
from utils import load_recipes

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


def prepare_working_dir(working_dir : str): 
    # Create directory structure
    # Create empty localhost file if it does not exist
    pass


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

def get_infra_path(infra_name : str, working_dir : str) -> str:
    infra_path = os.path.join(working_dir, infra_name)

    if infra_name == "localhost":
        os.makedirs(os.path.dirname(infra_path), exist_ok=True)
        with open(infra_path, 'w') as inventory_file:
            inventory_file.write("[local]\nlocalhost ansible_connection=local\n")

    if not os.path.exists(infra_path): 
        raise NotADirectoryError(f"Cannot find an inventory file at {infra_path}. Please provision the infrastructure first.")

    return infra_path



def provision(infra : str, provider : str, recipe : str):
    pass

def configure(infra_path : str, recipe_metadata : Dict[str, str]): 
    recipe_dir = recipe_metadata.get("recipe_dir")
    if not recipe_dir: 
        raise ValueError(f"Should not happen. recipe_dir does not exist in manifest: {recipe_metadata}")

    recipe_runtime = recipe_metadata.get("recipe_runtime")
    recipe_entry = recipe_metadata.get("recipe_entry", "bash")
    if recipe_runtime == "ansible":
        ansible_runner(infra_path, recipe_entry, recipe_dir)
    elif recipe_runtime == "bash":
        raise NotImplementedError("Bash runner is not implemented")
    else:
        raise ValueError(f"Unknown recipe runtime: {recipe_runtime}")

 

def main():
    # Parse system args
    args = parse_sys_args()
    # Setup paths, prepare working directory, and load recipes
    script_dir = os.path.dirname(os.path.abspath(__file__))    
    working_dir = os.path.abspath(args.directory) if os.path.isabs(args.directory) else os.path.join(script_dir, args.directory)
    recipe_dirs = prepare_dir_list(args.recipe_path, default_recipe_dirs)

    # Prepare working directory
    prepare_working_dir(working_dir)
    # Detect and load all the recipes
    provision_recipes, configure_recipes = load_recipes(recipe_dirs)

    if args.cmd == "provision":
        # Throw if the required provision_recipe is not available
        if args.recipe not in provision_recipes:
            raise ValueError(f"Provision recipe '{args.recipe}' does not exist.")
        provision(args.infra, args.provider, args.recipe)
    elif args.cmd == "configure":
        # Throw if the required configure recipe is not available
        if args.recipe not in configure_recipes:
            raise ValueError(f"Configure recipe '{args.recipe}' does not exist.")
        recipe_metadata = configure_recipes[args.recipe]
        infra_path = get_infra_path(args.infra, working_dir)
        configure(infra_path, recipe_metadata) 

    

    # print("Welcome to Stack Starter!")
    # Add your CLI logic here

if __name__ == "__main__":
    main()
