import argparse

def parse_sys_args():
    # Setup top level parser
    parser = argparse.ArgumentParser(description="A utility for provision machines and configure software stacks based on predefined recipes")
    parser.add_argument("infra", help="Name of the infrastructure to provision or configure", default="localhost")
    parser.add_argument("-d", "--directory", help="Specify the working directory", default="/tmp/stack_starter/")
    subparsers = parser.add_subparsers(title="CMD", description="Sub-commands")

    # Setup sub-parser for provision sub-command
    parser_provision = subparsers.add_parser("provision", description="Provision machines and networks from bare metal or cloud providers", epilog="Return an Ansible hostfile of the provisioned machines")
    parser_provision.add_argument("provider", help="Infrastructure provider for the machines to provision", default="localhost")
    parser_provision.add_argument("recipe", help="Recipe for provisioning")
    parser_provision.set_defaults(cmd="provision")

    # Setup sub-parser for configure sub-command
    parser_configure = subparsers.add_parser("configure", description="Configure software stack on a specified infrastructure")
    parser_configure.add_argument("recipe", help="Recipe for configure the infrastructure")
    parser_configure.set_defaults(cmd="configure")
    
    # Parse and return arguments in Name space object
    # Example: Namespace(infra='home', directory='/tmp/stack_starter/', recipe='mac_os_host', cmd='configure')
    return parser.parse_args()

def provision(provider : str, recipe : str):
    print(f"Provider: {provider}")
    print(f"Recipe: {recipe}")
    pass

def configure(recipe : str): 
    print(f"Recipe: {recipe}")
    pass

def main():
    args = parse_sys_args()

    if args.cmd == "provision":
        provision(args.provider, args.recipe)
    elif args.cmd == "configure":
        configure(args.recipe) 

    

    # print("Welcome to Stack Starter!")
    # Add your CLI logic here

if __name__ == "__main__":
    main()