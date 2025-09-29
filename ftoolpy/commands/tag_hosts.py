## Tag hosts with a specified tag using FalconPy

# Take a list of hostnames and add or remove a tag from each host.

import argparse
import os
from ftoolpy.auth import get_client

def register_subcommand(subparsers):
    parser = subparsers.add_parser(
        "tag-hosts",
        help="Add or remove a tag from a list of hosts using FalconPy",
        description="Add or remove a tag from a list of hosts using FalconPy"
    )
    parser.add_argument(
        "-i", "--input-file",
        required=True,
        help="Path to the input file containing hostnames (one per line)"
    )
    parser.add_argument(
        "-t", "--tag",
        required=True,
        help="The tag to add or remove"
    )
    parser.add_argument(
        "-a", "--action",
        choices=["add", "remove"],
        default="add",
        required=False,
        help="Action to perform: add or remove the tag"
    )
    parser.set_defaults(func=tag_hosts)

def tag_hosts(args):
    # Initialize Falcon instance
    falcon = get_client()

    # Read hostnames from input file
    if not os.path.isfile(args.input_file):
        print(f"Input file {args.input_file} does not exist.")
        return

    with open(args.input_file, 'r') as f:
        hostnames = [line.strip() for line in f if line.strip()]

    if not hostnames:
        print("No hostnames found in the input file.")
        return
    
    # Ensure the tag begins with FalconGroupingTag/<tag>
    if not args.tag.startswith("FalconGroupingTags/"):
        args.tag = f"FalconGroupingTags/{args.tag}"
    
    print(f"Processing {len(hostnames)} hosts to {args.action} tag '{args.tag}'")

    for hostname in hostnames:
        try:
            # Query device by hostname to get the device ID
            response = falcon.command("QueryDevicesByFilter", filter=f"hostname:'{hostname}'")
            if response["status_code"] == 200 and response["body"]["resources"]:
                device_id = response["body"]["resources"][0]
                body = {
                    "action": args.action,
                    "device_ids": [device_id],
                    "tags": [args.tag]
                }
                # Add or remove the tag
                tag_response = falcon.command("UpdateDeviceTags", body=body)

                if tag_response["body"]["code"] == 200:
                    print(f"Successfully {args.action}ed tag '{args.tag}' for host '{hostname}' (ID: {device_id})")
                else:
                    print(f"Failed to {args.action} tag '{args.tag}' for host '{hostname}' (ID: {device_id}): {tag_response}")
            else:
                print(f"Host '{hostname}' not found.")
        except Exception as e:
            print(f"Unexpected error for host '{hostname}': {str(e)}")
            continue
    print("Tagging operation completed.")

# Example usage: 
# ftool tag-hosts -i hostnames.txt -t "Critical" -a add
# ftool tag-hosts -i hostnames.txt -t "Critical" -a remove