import argparse
import os
from typing_extensions import Dict
from .runners import ansible_runner, bash_runner, vagrant_runner
from .utils import load_recipes, prepare_dir_list, prepare_working_dir, get_infra_path

default_recipe_dirs = [
    "./recipes",
    "/tmp/stack_starter/recipes"
]

# argparser custom action for parsing key-value arguments
class keyvalue(argparse.Action): 
    # Constructor calling 
    def __call__( self , parser, namespace, 
                 values : list[str], option_string = None): 
        setattr(namespace, self.dest, dict()) 
          
        for value in values: 
            # split it into key and value 
            key, value = value.split('=') 
            # assign into dictionary 
            getattr(namespace, self.dest)[key] = value 

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
    parser_provision.add_argument('--kwargs', nargs="*", action = keyvalue, help="List of key-value arguments to pass to the provision recipe. Use key=value syntax.")
    parser_provision.set_defaults(cmd="provision")

    # Setup sub-parser for configure sub-command
    parser_configure = subparsers.add_parser("configure", description="Configure software stack on a specified infrastructure")
    parser_configure.add_argument("infra", help="Name of the infrastructure to configure. Use localhost to configure the current machine.", default="localhost")
    parser_configure.add_argument("recipe", help="Recipe for configure the infrastructure")
    parser_configure.add_argument('--kwargs', nargs="*", action = keyvalue, help="List of key-value arguments to pass to the provision recipe. Use key=value syntax.")
    parser_configure.set_defaults(cmd="configure")

    # Setup sub-parser for recipe management sub-command
    parser_recipe = subparsers.add_parser("recipe", description="Manage recipes")
    
    # Parse and return arguments in Name space object
    # Example: Namespace(infra='home', directory='/tmp/stack_starter/', recipe='mac_os_host', cmd='configure')
    return parser.parse_args()


def provision(infra_name : str, infra_provider : str, recipe_metadata : Dict[str, str], working_dir : str, kwargs : Dict[str, str]):
    recipe_dir = recipe_metadata.get("recipe_dir")
    if not recipe_dir: 
        raise ValueError(f"Should not happen. recipe_dir does not exist in manifest: {recipe_metadata}")

    recipe_runtime = recipe_metadata.get("recipe_runtime")
    recipe_entry = recipe_metadata.get("recipe_entry", "bash")
    if recipe_runtime == "vagrant":
        vagrant_runner(infra_name, infra_provider, recipe_entry, recipe_dir, working_dir, kwargs)

def configure(infra_path : str, recipe_metadata : Dict[str, str], kwargs : Dict[str, str]): 
    recipe_dir = recipe_metadata.get("recipe_dir")
    if not recipe_dir: 
        raise ValueError(f"Should not happen. recipe_dir does not exist in manifest: {recipe_metadata}")

    recipe_runtime = recipe_metadata.get("recipe_runtime")
    recipe_entry = recipe_metadata.get("recipe_entry", "bash")
    if recipe_runtime == "ansible":
        ansible_runner(infra_path, recipe_entry, recipe_dir, kwargs)
    elif recipe_runtime == "bash": 
        bash_runner(infra_path, recipe_entry, recipe_dir, kwargs)
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
        recipe_metadata = provision_recipes[args.recipe]
        provision(args.infra, args.provider, recipe_metadata, working_dir, args.kwargs)
    elif args.cmd == "configure":
        # Throw if the required configure recipe is not available
        if args.recipe not in configure_recipes:
            raise ValueError(f"Configure recipe '{args.recipe}' does not exist.")
        recipe_metadata = configure_recipes[args.recipe]
        infra_path = get_infra_path(args.infra, working_dir)
        configure(infra_path, recipe_metadata, args.kwargs) 

    

    # print("Welcome to Stack Starter!")
    # Add your CLI logic here

if __name__ == "__main__":
    main()
