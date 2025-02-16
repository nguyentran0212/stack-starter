import os
import yaml
import subprocess
from typing import List, Tuple
from typing_extensions import Dict

def prepare_dir_list(dir: str, default_dirs: List[str] = []) -> List[str]:
    """
    Prepare a list of valid directory paths.

    Args:
        dir (str): The directory path to validate and include.
        default_dirs (List[str], optional): A list of default directory paths to include. Defaults to [].

    Returns:
        List[str]: A list of absolute paths to valid directories.
    """
    valid_dirs = []
    combined_dirs = [dir] + default_dirs

    for dir in combined_dirs:
        if os.path.isabs(dir):
            valid_dirs.append(dir)
        else:
            valid_dirs.append(os.path.abspath(os.path.join(os.getcwd(), dir)))

    return valid_dirs


def load_recipes(recipe_dirs: List[str]) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Load recipes from specified directories.

    Args:
        recipe_dirs (List[str]): A list of directories to search for recipe manifests.

    Returns:
        Tuple[Dict[str, Dict], Dict[str, Dict]]: Two dictionaries containing provision and configure recipes.
    """
    provision_recipes = {}
    configure_recipes = {}

    def process_recipe_dir(recipe_dir: str):
        for root, _, files in os.walk(recipe_dir):
            for file in files:
                if file == "manifest.yaml":
                    manifest_path = os.path.join(root, file)
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = yaml.safe_load(f)
                            recipe_name = manifest.get('name')
                            recipe_type = manifest.get('recipe_type')
                            manifest["recipe_dir"] = os.path.dirname(manifest_path) # Add directory containing the recipe directory
                            
                            if recipe_type == 'provision':
                                provision_recipes[recipe_name] = manifest
                            elif recipe_type == 'configure':
                                configure_recipes[recipe_name] = manifest
                    except yaml.YAMLError as e:
                        print(f"Error loading YAML file {manifest_path}: {e}")

    for recipe_dir in recipe_dirs:
        process_recipe_dir(recipe_dir)

    return provision_recipes, configure_recipes

def prepare_working_dir(working_dir: str):
    """
    Prepare the working directory by creating necessary subdirectories and files.

    Args:
        working_dir (str): The path to the working directory.
    """
    # Create directory structure
    os.makedirs(working_dir, exist_ok=True)
    os.makedirs(os.path.join(working_dir, "recipes"), exist_ok=True)

    # Create empty localhost file if it does not exist
    os.makedirs(os.path.join(working_dir, "localhost"), exist_ok=True)
    with open(os.path.join(working_dir, "localhost", "hosts.ini"), 'w') as inventory_file:
        inventory_file.write("[local]\nlocalhost ansible_connection=local\n")


def get_infra_path(infra_name: str, working_dir: str) -> str:
    """
    Get the path to the infrastructure inventory file.

    Args:
        infra_name (str): The name of the infrastructure.
        working_dir (str): The path to the working directory.

    Returns:
        str: The path to the infrastructure inventory file.

    Raises:
        NotADirectoryError: If the inventory file does not exist.
    """
    infra_path = os.path.join(working_dir, infra_name)

    # if infra_name == "localhost":
    #     os.makedirs(os.path.dirname(infra_path), exist_ok=True)
    #     with open(infra_path, 'w') as inventory_file:
    #         inventory_file.write("[local]\nlocalhost ansible_connection=local\n")

    if not os.path.exists(infra_path): 
        raise NotADirectoryError(f"Cannot find an inventory file at {infra_path}. Please provision the infrastructure first.")

    return infra_path

def pull_repo(url : str, recipe_dir : str, force = False): 
    os.chdir(recipe_dir)
    command = [
        "git",
        "clone",
        "--depth=1",
        url
    ]
    subprocess.run(command, check=True)

def create_starter_recipe(recipe : str, dir : str):
    starter_recipes = {
        "configure-bash" : "./recipes/configure/sample_configure_bash/",
        "configure-ansible" : "./recipes/configure/sample_configure_ansible/",
        "provision-vagrant" : "./recipes/provision/sample_provision_vagrant/"
    }
    
    if recipe not in starter_recipes:
        raise ValueError(f"Unknown starter recipe requested. Available recipes: {starter_recipes.keys()}")

    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(dir, exist_ok=True)

    command = [
        "cp",
        "-r", 
        os.path.join(script_dir, str(starter_recipes.get(recipe))),
        dir
    ]
    subprocess.run(command, check=True)

def print_recipe(recipe_metadata : dict[str, str]):
    print("=============")
    print(f'Recipe: {recipe_metadata.get("name")}')
    print(f' |--Version: {recipe_metadata.get("version", "N/A")}')
    print(f' |--Homepage: {recipe_metadata.get("homepage", "N/A")}')
    print(f' |--Repo URL: {recipe_metadata.get("repository_url", "N/A")}')
    print(f' |--Directory: {recipe_metadata.get("recipe_dir")}')
    print(f' |--Runtime: {recipe_metadata.get("recipe_runtime")}')
    print(f' |--Entry: {recipe_metadata.get("recipe_entry")}')

def set_provision_env_variables(infra_name : str, infra_provider : str, working_dir : str):
    os.environ['STACK_STARTER_INFRA_NAME'] = infra_name
    os.environ['STACK_STARTER_INFRA_PROVIDER'] = infra_provider
    os.environ["STACK_STARTER_WORKING_DIR"] = working_dir


