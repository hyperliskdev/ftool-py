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

    # Map hostnames to IDs and check their online status
    response = falcon.command("QueryDevicesByFilter", filter=f"hostname:['" + "','".join(hostnames) + "']")

    # Check if the response is valid and contains resources
    if response["status_code"] == 200 and response["body"]["resources"]:

        # Create a mapping of hostname to device_id
        # host_id_map = {item["hostname"]: item["device_id"] for item in response["body"]["resources"]}
        host_ids = response["body"]["resources"]

        device_details = falcon.command("PostDeviceDetailsV2", ids=host_ids)

        # Check if the device details response is valid
        if device_details["status_code"] == 200 and host_ids:

            # Create a mapping of device_id to its details
            device_info_map = {item["device_id"]: item for item in device_details["body"]["resources"]}
            for hostname in hostnames:
                host_id = host_id_map.get(hostname, "N/A")
                if host_id != "N/A":
                    device_info = device_info_map.get(host_id, {})
                    first_seen = device_info.get("first_seen", "Unknown")
                    last_seen = device_info.get("last_seen", "Unknown")
                    results.append((hostname, host_id, first_seen, last_seen))
                    print(f"Host: {hostname}, ID: {host_id}, First Seen: {first_seen}, Last Seen: {last_seen}")
                else:
                    results.append((hostname, "N/A", "Not Found"))
                    print(f"Host: {hostname}, ID: N/A, Not Found")
        else:
            print(f"Error retrieving device details: {response}")

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