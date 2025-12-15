## Tag hosts with a specified tag using FalconPy

# Take a list of hostnames or IP addresses and add or remove a tag from each host.

import argparse
import ipaddress
import logging
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
        help="Path to the input file containing hostnames, IPv4 or IPv6 addresses (one per line)"
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

def is_ip_address(value):
    """Check if a string is a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False

def tag_hosts(args):
    # Initialize Falcon instance
    falcon = get_client()

    # Read hostnames/IP addresses from input file
    if not os.path.isfile(args.input_file):
        print(f"Input file {args.input_file} does not exist.")
        return

    with open(args.input_file, 'r') as f:
        hostnames = [line.strip() for line in f if line.strip()]

    if not hostnames:
        print("No hostnames or IP addresses found in the input file.")
        return
    
    # Ensure the tag begins with FalconGroupingTag/<tag>
    if not args.tag.startswith("FalconGroupingTags/"):
        args.tag = f"FalconGroupingTags/{args.tag}"
    
    print(f"Processing {len(hostnames)} hosts to {args.action} tag '{args.tag}'")

    for hostname in hostnames:
        try:
            # Determine if the input is an IP address or hostname
            if is_ip_address(hostname):
                # Query device by IP address
                filter_query = f"local_ip:'{hostname}'"
                identifier_type = "IP address"
            else:
                # Query device by hostname
                filter_query = f"hostname:'{hostname}'"
                identifier_type = "hostname"

            response = falcon.command("QueryDevicesByFilter", filter=filter_query)
            logging.debug(f"QueryDevicesByFilter response for '{hostname}': {response}")

            if response["status_code"] == 200 and response["body"]["resources"]:
                device_id = response["body"]["resources"][0]
                body = {
                    "action": args.action,
                    "device_ids": [device_id],
                    "tags": [args.tag]
                }
                # Add or remove the tag
                tag_response = falcon.command("UpdateDeviceTags", body=body)
                logging.debug(f"UpdateDeviceTags response for '{hostname}': {tag_response}")

                if tag_response["status_code"] == 202:
                    print(f"Success! {args.action} tag '{args.tag}' to {identifier_type} '{hostname}' (ID: {device_id})")
                else:
                    print(f"Failure! {args.action} tag '{args.tag}' {identifier_type} '{hostname}' (ID: {device_id}): {tag_response}")
            else:
                print(f"{identifier_type.capitalize()} '{hostname}' not found.")
        except Exception as e:
            print(f"Unexpected error for host '{hostname}': {str(e)}")
            continue
    print("Tagging operation completed.")

# Example usage:
# ftool tag-hosts -i hosts.txt -t "Critical" -a add
# ftool tag-hosts -i hosts.txt -t "Critical" -a remove
# Input file can contain hostnames, IPv4 addresses, or IPv6 addresses (one per line)