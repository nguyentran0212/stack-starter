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

def bash_runner(infra_path : str, script : str, recipe_dir : str):
    _, tail = os.path.split(infra_path)
    if tail != "localhost":
        raise ValueError(f"Bash runner only works with localhost. Provided infrastructure: {infra_path}")
    
    os.chdir(str(recipe_dir)) 
    bash_command = [
        "bash",
        script
    ]
    subprocess.run(bash_command, check=True)

def vagrant_runner(infra_name: str, infra_provider : str, recipe_entry : str, recipe_dir : str):
    pass
