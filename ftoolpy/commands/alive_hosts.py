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
    parser.add_argument(
        "-d", "--dead",
        required=False,
        action='store_true',
        help="Show only hosts that are offline"
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
    
    
    for hostname in hostnames:
        
        response = falcon.command("QueryDevicesByFilter", filter=f"hostname:'{hostname}'")
        
        if response["status_code"] == 200 and response["body"]["resources"]:
            host_id = response["body"]["resources"][0]
            device_details = falcon.command("GetDeviceDetails", ids=[host_id])
            if device_details["status_code"] == 200 and device_details["body"]["resources"]:
                device_info = device_details["body"]["resources"][0]
                last_seen = device_info.get("last_seen", None)
                first_seen = device_info.get("first_seen", None)
                results.append((hostname, host_id, last_seen, first_seen))
            else:
                print(f"Error retrieving device details for '{hostname}': {device_details}")
        else:
            print(f"Hostname '{hostname}' not found in Falcon Console, checking if hidden...")
            hidden_devices = falcon.command("QueryHiddenDevices", filter=f"hostname:'{hostname}'", limit=5000)
            if hidden_devices["status_code"] == 200 and hidden_devices["body"]["resources"]:
                hidden_host_id = hidden_devices["body"]["resources"][0]
                hidden_device_details = falcon.command("GetDeviceDetails", ids=[hidden_host_id])
                if hidden_device_details["status_code"] == 200 and hidden_device_details["body"]["resources"]:
                    hidden_info = hidden_device_details["body"]["resources"][0]
                    results.append((hostname, hidden_host_id, "Hidden Device", "Hidden Device"))
                else:
                    print(f"Error retrieving hidden device details for '{hostname}': {hidden_device_details}")
            else:
                print(f"Hostname '{hostname}' not found as hidden device either.")
                results.append((hostname, "N/A", "N/A", "N/A"))
   
    #Filter for hosts that aren't in results
    if args.dead:
        alive_hostnames = {result[0] for result in results}
        dead_hostnames = set(hostnames) - alive_hostnames
        results = [(hostname, "N/A", "N/A", "N/A") for hostname in dead_hostnames]

    for res in results:
        print(f"Hostname: {res[0]}, ID: {res[1]}, Last Seen: {res[2]}, First Seen: {res[3]}")
        
    
    # Write results to output file if specified
    if args.output_file:
        try:
            with open(args.output_file, 'w') as f:
                for hostname, host_id, last_seen, first_seen in results:
                    f.write(f"{hostname},{host_id},{last_seen},{first_seen}\n")
            print(f"Results saved to {args.output_file}")
        except Exception as e:
            print(f"Failed to write to output file {args.output_file}: {str(e)}")

# Example usage:
# python ftool.py alive-hosts -i host_ids.txt -o results.csv