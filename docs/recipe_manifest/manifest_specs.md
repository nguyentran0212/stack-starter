# Recipe Manifest Specification

Last updated: 25/11/2024

`stack-starter` runs user-defined recipes for provisioning computing nodes ansible configuring software stacks. A `manifest.yaml` file provides `stack-starter` the necessary information to run a recipe (e.g., should it use bash or ansible? If it is going to use bash, which script within the recipe should be called? If it is going to use ansible, which script should be called?).

## Fields

Every package must have a `manifest.yaml` file to be detected as a recipe. This file must contain the following fields:

Metadata: 

- `name : str`: name of the recipe. 
- `version : str`: a string showing the version of the recipe. Semantic Versioning is expected.
- `homepage : str` (optional): a URL of the recipe homepage (e.g., GitHub repository)
- `repository_url : str` (optional): a URL to the git repository of the recipe
- `recipe_type : str`: type of recipe. Allowed values: `provision`, `configure`
- `recipe_runtime : str`: name of the tool required for running the recipe. Allowed values: `bash`, `ansible`, `vagrant`
- `recipe_entry : str`: name of the entry point for running the recipe (e.g., bash script, ansible playbook, vagrant file)
