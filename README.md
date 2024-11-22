# stack-starter

`stack-starter` is a utility to automate the provisioning and configuration of a machine cluster according to predefined recipes. It aims to make it easier for developers to provision machines and deploy desired software stacks on them in a consistent and repeatable manner. This utility comes with a predefined set of recipes. User can provide recipes in form of Ansible or Bash script.

## Installation

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
    pip install stack-starter
    ```

## Available recipes

### Provision

### Configure

- `mac_arm_starter`: macOS rice with `ZSH`, `nvim`, `kitty` terminal emulator, tiling manager `yabai`, hotkey daemon `skhd`, `sketchybar` and `borders`. Tested on macOS 14. 

