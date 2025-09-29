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
        host_ids = [line.strip() for line in f if line.strip()]

    if not host_ids:
        print("No host IDs found in the input file.")
        return

    results = []
    for host_id in host_ids:
        try:
            response = falcon.query_devices_by_id(ids=[host_id])
            if response["status_code"] == 200 and response["body"]["resources"]:
                device_info = response["body"]["resources"][0]
                status = device_info.get("status", "Unknown")
                results.append((host_id, status))
                print(f"Host ID: {host_id}, Status: {status}")
            else:
                results.append((host_id, "Not Found"))
                print(f"Host ID: {host_id}, Status: Not Found")
        except Exception as e:
            results.append((host_id, f"Error: {str(e)}"))
            print(f"Host ID: {host_id}, Error: {str(e)}")

    # Write results to output file if specified
    if args.output_file:
        try:
            with open(args.output_file, 'w') as f:
                for host_id, status in results:
                    f.write(f"{host_id},{status}\n")
            print(f"Results saved to {args.output_file}")
        except Exception as e:
            print(f"Failed to write to output file {args.output_file}: {str(e)}")

# Example usage:
# python ftool.py alive-hosts -i host_ids.txt -o results.csv