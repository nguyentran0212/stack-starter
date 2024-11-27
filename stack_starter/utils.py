import os
import yaml
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
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for dir in combined_dirs:
        if os.path.isabs(dir):
            valid_dirs.append(dir)
        else:
            valid_dirs.append(os.path.abspath(os.path.join(script_dir, dir)))

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
    # Create empty localhost file if it does not exist
    pass


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

    if infra_name == "localhost":
        os.makedirs(os.path.dirname(infra_path), exist_ok=True)
        with open(infra_path, 'w') as inventory_file:
            inventory_file.write("[local]\nlocalhost ansible_connection=local\n")

    if not os.path.exists(infra_path): 
        raise NotADirectoryError(f"Cannot find an inventory file at {infra_path}. Please provision the infrastructure first.")

    return infra_path

def set_provision_env_variables(infra_name : str, infra_provider : str, working_dir : str):
    os.environ['STACK_STARTER_INFRA_NAME'] = infra_name
    os.environ['STACK_STARTER_INFRA_PROVIDER'] = infra_provider
    os.environ["STACK_STARTER_WORKING_DIR"] = working_dir

