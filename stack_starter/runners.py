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
    os.environ['STACK_STARTER_INFRA_NAME'] = infra_name
    os.environ['STACK_STARTER_INFRA_PROVIDER'] = infra_provider

    os.chdir(str(recipe_dir))
    vagrant_command = [
        "vagrant",
        "up",
        "--provider",
        infra_provider,
        "--vagrantfile",
        recipe_entry
    ]
    result = subprocess.run(vagrant_command, check=False)
    if result.returncode != 0:
        raise RuntimeError("Vagrant command failed with exit code {}".format(result.returncode))
