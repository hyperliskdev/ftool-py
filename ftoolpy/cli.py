import argparse
from ftoolpy.commands import alive_hosts, tag_hosts  # Import your command modules here

def main():
    parser = argparse.ArgumentParser(prog="ftool-py", description="Falcon CLI powered by falconpy")
    subparsers = parser.add_subparsers(title="commands", description="Available commands")

    # Register subcommands here
    alive_hosts.register_subcommand(subparsers)
    tag_hosts.register_subcommand(subparsers)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()