import os
import yaml
from typing import List, Tuple
from typing_extensions import Dict

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
