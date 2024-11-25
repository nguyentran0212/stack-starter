import os
import subprocess

def ansible_runner(infra_path : str, playbook : str, recipe_dir : str):
    os.chdir(str(recipe_dir)) 
    
    ansible_command = [
        "ansible-playbook",
        playbook,
        "-i", infra_path,
        "-vv",
        # "--ask-become-pass"
    ]
    
    subprocess.run(ansible_command, check=True)
