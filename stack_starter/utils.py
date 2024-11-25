import os
import yaml
from typing import List, Tuple
from typing_extensions import Dict

def prepare_dir_list(dir : str, default_dirs : List[str] = []) -> List[str]:
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

def prepare_working_dir(working_dir : str): 
    # Create directory structure
    # Create empty localhost file if it does not exist
    pass


def get_infra_path(infra_name : str, working_dir : str) -> str:
    infra_path = os.path.join(working_dir, infra_name)

    if infra_name == "localhost":
        os.makedirs(os.path.dirname(infra_path), exist_ok=True)
        with open(infra_path, 'w') as inventory_file:
            inventory_file.write("[local]\nlocalhost ansible_connection=local\n")

    if not os.path.exists(infra_path): 
        raise NotADirectoryError(f"Cannot find an inventory file at {infra_path}. Please provision the infrastructure first.")

    return infra_path
