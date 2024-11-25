# stack-starter

`stack-starter` is a utility to automate the provisioning and configuration of a machine cluster according to predefined recipes. It aims to make it easier for developers to provision machines and deploy desired software stacks on them in a consistent and repeatable manner. `stack-starter` is extensible via user-defined recipes. 

## Concept

Think of `stack-starter` as a USB stick for setting up a new OS, but instead of setting up a new OS, it sets up a distributed system, and instead of a USB stick, it's a CLI utility that runs on a controller computer. `stack-starter` applies recipes to provision machines and configure software stack. 

**Provision** in this context means the process of creating VMs and networks, and setting up the OS and network stacks so that VMs are up and ready for software deployment. A set of VMs and the corresponding network is considered an **Infrastructure**.

**Configure** in this context means the process of deploying software stack on an infrastructure. 

**Recipe** is a collection of bash scripts or IaaS scripts that defines how a provisioning or configuration task is done. Each recipe has a `manifest.json` file, which defines how it should be interpreted and invoked. `stack-starter` is able to run bash script on localhost and run ansible on both local and remote hosts out of the box. More runner can be added in the future. 


## Installation

We use `pipx` to make the `stack-starter` utility available in terminal without modifying the python packages at the system level.

### macOS


1. Install `pipx` if you haven't already:

    ```bash
    brew install pipx
    pipx ensurepath
    ```

2. Use `pipx` to install `ansible`:

    ```bash
    pipx install ansible
    ```

3. Install `stack-starter`:

    ```bash
    pipx install stack-starter
    ```

### GNU/Linux based systems

TBA


## Usage

```bash
# Use a recipe to provision an infrastructure and store the info in an Ansible hostfile named infra_name
stack-starter provision infra_name recipe_name

# Use a recipe to configure localhost
stack-starter configure localhost recipe_name

# Use a recipe to configure infrastructure in an ansible hostfile called infra_name
stack-starter configure infra_name recipe_name
```


## Available recipes

Built-in recipes are stored in `stack_starter/recipes/configure` and `stack_starter/recipes/provision`

### Provision

Provision recipes handle the creation

- TBA

### Configure

- `mac_arm_starter`: macOS rice with `ZSH`, `nvim`, `kitty` terminal emulator, tiling manager `yabai`, hotkey daemon `skhd`, `sketchybar` and `borders`. Tested on macOS 14. 


## Contribute

### Setup a development environment

This project use `poetry` to manage dependencies and build package. Install `poetry` if you haven't. 

```bash
poetry install  # Install dependencies
source .venv/bin/activate  # Activate poetry venv
stack-starter -h  # Should be accessible and working
```

### Recipe development instruction

Built-in recipes are stored in the `stack-starter/recipes` folder by default. User can tell stack-starter to look for recipes at more folders by adding `-r DIRECTORY` argument when using the CLI. 

Each recipe is a folder which contains a `manifest.json` file. Information inside manifest is used to identify and run recipe.[Manifest instruction](docs/recipe_manifest/manifest_specs.md). 

