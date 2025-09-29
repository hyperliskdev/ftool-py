# Check the status of a list of hosts using FalconPy
import os
import argparse
from ftoolpy.auth import get_client


def register_subcommand(subparsers):
    parser = subparsers.add_parser(
        "alive-hosts",
        help="Check the status of a list of hosts using FalconPy",
        description="Check the status of a list of hosts using FalconPy"
    )
    parser.add_argument(
        "-i", "--input-file",
        required=True,
        help="Path to the input file containing host IDs (one per line)"
    )
    parser.add_argument(
        "-o", "--output-file",
        required=False,
        help="Path to the output file to save results (optional)"
    )
    parser.set_defaults(func=check_alive_hosts)


def check_alive_hosts(args):
    # Initialize Falcon instance
    falcon = get_client()

    # Read host IDs from input file
    if not os.path.isfile(args.input_file):
        print(f"Input file {args.input_file} does not exist.")
        return

    with open(args.input_file, 'r') as f:
        hostnames = [line.strip() for line in f if line.strip()]

    if not hostnames:
        print("No hostnames found in the input file.")
        return


    results = []
    ## Use QueryDevicesByFilter to find host_ids based on hostnames
    for hostname in hostnames:
        response = falcon.command("QueryDevicesByFilter",filter=f"name:'{hostname}'")
        if response["status_code"] == 200 and response["body"]["resources"]:
            host_id = response["body"]["resources"][0]
            device_details = falcon.get_device_details(ids=[host_id])
            if device_details["status_code"] == 200 and device_details["body"]["resources"]:
                device_info = device_details["body"]["resources"][0]
                online_status = device_info.get("online", "Unknown")
                results.append((hostname, host_id, online_status))
                print(f"Host: {hostname}, ID: {host_id}, Online: {online_status}")
            else:
                results.append((hostname, "N/A", "Error retrieving details"))
                print(f"Host: {hostname}, ID: N/A, Error retrieving details")
        else:
            results.append((hostname, "N/A", "Not Found"))
            print(f"Host: {hostname}, ID: N/A, Not Found")
            continue

    # Write results to output file if specified
    if args.output_file:
        try:
            with open(args.output_file, 'w') as f:
                for hostname, host_id, online_status in results:
                    f.write(f"{hostname},{host_id},{online_status}\n")
            print(f"Results saved to {args.output_file}")
        except Exception as e:
            print(f"Failed to write to output file {args.output_file}: {str(e)}")

# Example usage:
# python ftool.py alive-hosts -i host_ids.txt -o results.csv