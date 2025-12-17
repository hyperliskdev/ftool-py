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
    hidden_results = []
    ## Use QueryDevicesByFilter to find host_ids based on hostnames

    # Map hostnames to IDs and check their online status
    response = falcon.command("QueryDevicesByFilter", filter=f"hostname:['" + "','".join(hostnames) + "']", limit=5000)
    hidden_devices = falcon.command("QueryHiddenDevices", filter=f"hostname:['" + "','".join(hostnames) + "']", limit=5000)
    
    # Check if the response is valid and contains resources
    if response["status_code"] == 200 and response["body"]["resources"] and hidden_devices["status_code"] == 200:
        
        hidden_host_ids = hidden_devices["body"]["resources"]

        if len(hidden_host_ids) > 0:
            hidden_device_details = falcon.command("PostDeviceDetailsV2", ids=hidden_host_ids)
            
            if hidden_device_details["status_code"] == 200 and hidden_device_details["body"]["resources"]:
                hidden_details = hidden_device_details["body"]["resources"]
                
                for hidden_device in hidden_details:
                    hostname = hidden_device.get("hostname", "Unknown")
                    host_id = hidden_device.get("device_id", "Unknown")
                    hidden = "Device is hidden in Falcon Console"
                    hidden_results.append((hostname, host_id, hidden))
                    
            else:
                print(f"Error retrieving hidden device details: {hidden_device_details}")
        else:
            print("No hidden devices found.")
        
        host_ids = response["body"]["resources"]

        device_details = falcon.command("PostDeviceDetailsV2", ids=host_ids)
        # Check if the device details response is valid
        if device_details["status_code"] == 200 and device_details["body"]["resources"]:

            device_details = device_details["body"]["resources"]

            # Check each device details and determine online status
            for device in device_details:
                hostname = device.get("hostname", "Unknown")
                host_id = device.get("device_id", "Unknown")
                last_seen = device.get("last_seen", None)
                first_seen = device.get("first_seen", None)
                results.append((hostname, host_id, last_seen, first_seen))
        else:
            print(f"Error retrieving device details: {response}")
            
    #Filter for hosts that aren't in results
    if args.dead:
        alive_hostnames = {result[0] for result in results}
        dead_hostnames = set(hostnames) - alive_hostnames
        results = [(hostname, "N/A", "N/A", "N/A") for hostname in dead_hostnames]
        

    for res in results:
        print(f"Hostname: {res[0]}, ID: {res[1]}, Last Seen: {res[2]}, First Seen: {res[3]}")
    for hidden_res in hidden_results:
        print(f"Hostname: {hidden_res[0]}, ID: {hidden_res[1]}, Status: {hidden_res[2]}")
        
    
    # Write results to output file if specified
    if args.output_file:
        try:
            with open(args.output_file, 'w') as f:
                for hostname, host_id, last_seen, first_seen in results:
                    f.write(f"{hostname},{host_id},{last_seen},{first_seen}\n")
                for hostname, host_id, hidden in hidden_results:
                    f.write(f"{hostname},{host_id},{hidden}\n")
            print(f"Results saved to {args.output_file}")
        except Exception as e:
            print(f"Failed to write to output file {args.output_file}: {str(e)}")

# Example usage:
# python ftool.py alive-hosts -i host_ids.txt -o results.csv