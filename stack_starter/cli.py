import argparse
import os
from typing_extensions import Dict
from .runners import ansible_runner, bash_runner, vagrant_runner
from .utils import load_recipes, prepare_dir_list, prepare_working_dir, get_infra_path, pull_repo, print_recipe, create_starter_recipe

script_dir = os.path.dirname(os.path.abspath(__file__))

default_recipe_dirs = [
    "/tmp/stack_starter/recipes", # Default tmp folder for storing recipes
    os.path.join(script_dir, "./recipes") # Starter / example recipes shipped with stack-starter
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
    # Setup top level parser `stack-starter`
    parser = argparse.ArgumentParser(description="A utility for provision machines and configure software stacks based on predefined recipes")
    parser.add_argument("-d", "--directory", help="Working directory for storing provisioning output", default="/tmp/stack_starter/")
    parser.add_argument("-r", "--recipe-path", help="Path to directory where recipes are stored", default="/tmp/stack_starter/recipes")
    subparsers = parser.add_subparsers(title="CMD", description="Sub-commands", required=True)

    # Setup sub-parser `stack-starter provision ...`
    parser_provision = subparsers.add_parser("provision", description="Provision machines and networks from bare metal or cloud providers", epilog="Return an Ansible hostfile of the provisioned machines")
    parser_provision.add_argument("infra", help="Name of the infrastructure to provision or configure")
    parser_provision.add_argument("provider", help="Infrastructure provider for the machines to provision")
    parser_provision.add_argument("recipe", help="Recipe for provisioning")
    parser_provision.add_argument('--kwargs', nargs="*", action = keyvalue, help="List of key-value arguments to pass to the provision recipe. Use key=value syntax.")
    parser_provision.set_defaults(cmd="provision")

    # Setup sub-parser for `stack-starter configure ...`
    parser_configure = subparsers.add_parser("configure", description="Configure software stack on a specified infrastructure")
    parser_configure.add_argument("infra", help="Name of the infrastructure to configure. Use localhost to configure the current machine.", default="localhost")
    parser_configure.add_argument("recipe", help="Recipe for configure the infrastructure")
    parser_configure.add_argument('--kwargs', nargs="*", action = keyvalue, help="List of key-value arguments to pass to the provision recipe. Use key=value syntax.")
    parser_configure.set_defaults(cmd="configure")

    # Setup sub-parser for `stack-starter recipe ...`
    parser_recipe = subparsers.add_parser("recipe", description="Manage recipes")
    parser_recipe.set_defaults(cmd="recipe")
    recipe_subparsers = parser_recipe.add_subparsers(title="Sub_CMD", description="Sub-commands for recipe management", required=True)
    # Sub-parser for `stack-starter recipe pull ...`
    parser_recipe_pull = recipe_subparsers.add_parser("pull", description="Pull recipe from a remote git repository")
    parser_recipe_pull.add_argument("url", help="URL of the Git repository of the recipe")
    parser_recipe_pull.set_defaults(recipe_cmd="pull")
    # Sub-parser for `stack-starter recipe list ...`
    parser_recipe_list = recipe_subparsers.add_parser("list", description="List the current recipes")
    parser_recipe_list.set_defaults(recipe_cmd="list")
    # Sub-parser for `stack-starter recipe create ...`
    parser_recipe_create = recipe_subparsers.add_parser("create", description="Create an starter recipe")
    parser_recipe_create.add_argument("recipe", help="Name of the sample recipe to create")
    parser_recipe_create.add_argument("dir", help="Directory to create the starter recipe")
    parser_recipe_create.set_defaults(recipe_cmd="create")
    
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
    else:
        raise ValueError(f"Unknown recipe requested: {recipe_runtime}")

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
        raise ValueError(f"Unknown recipe requested: {recipe_runtime}")
 

def main():
    # Parse system args
    args = parse_sys_args()
    # Setup paths, prepare working directory, and load recipes
    working_dir = os.path.abspath(args.directory) if os.path.isabs(args.directory) else os.path.join(os.getcwd(), args.directory)
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
    elif args.cmd == "recipe":
        if args.recipe_cmd == "pull":
            print(f"Pulling {args.url}...")
            pull_repo(args.url, recipe_dirs[0]) # Hard code to clone into the first directory in the recipe directory
        elif args.recipe_cmd == "list":
            print("PROVISION RECIPES...")
            for recipe in provision_recipes.values():
               print_recipe(recipe) 

            print("\nCONFIGURE RECIPES...")
            for recipe in configure_recipes.values():
               print_recipe(recipe) 
        elif args.recipe_cmd == "create":
            create_starter_recipe(args.recipe, args.dir)
            print(f"Starter recipe created at {args.dir}")


if __name__ == "__main__":
    main()
