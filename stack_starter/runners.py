import os
import subprocess
from .utils import set_provision_env_variables

def ansible_runner(infra_path : str, playbook : str, recipe_dir : str, kwargs : dict[str, str], inventory_file = "hosts.ini"):
    os.chdir(str(recipe_dir)) 
    ansible_command = [
        "ansible-playbook",
        playbook,
        "-i", os.path.join(infra_path, inventory_file), # Assume that inventory_file is hosts.ini underneath the infra_path
        "-vv",
        # "--ask-become-pass"
    ]
    subprocess.run(ansible_command, check=True)

def bash_runner(infra_path : str, script : str, recipe_dir : str, kwargs : dict[str, str]):
    _, tail = os.path.split(infra_path)
    if tail != "localhost":
        raise ValueError(f"Bash runner only works with localhost. Provided infrastructure: {infra_path}")
    
    os.chdir(str(recipe_dir)) 
    bash_command = [
        "bash",
        script
    ]
    subprocess.run(bash_command, check=True)

def vagrant_runner(infra_name: str, infra_provider : str, recipe_entry : str, recipe_dir : str, working_dir : str, kwargs : dict[str, str]):
    def validate_infra_provider(infra_provider : str):
        known_providers = ["virtualbox", "vmware_desktop", "vmware_fusion", "docker", "hyperv"]
        if infra_provider not in known_providers:
            return "virtualbox"
        else:
            return infra_provider

    infra_provider = validate_infra_provider(infra_provider)
    set_provision_env_variables(infra_name, infra_provider, working_dir) 

    os.environ["VAGRANT_VAGRANTFILE"] = recipe_entry

    os.chdir(str(recipe_dir))
    vagrant_command = [
        "vagrant",
        "up",
        "--provider",
        infra_provider,
    ]
    print(vagrant_command)
    result = subprocess.run(vagrant_command, check=False)
    if result.returncode != 0:
        raise RuntimeError("Vagrant command failed with exit code {}".format(result.returncode))
