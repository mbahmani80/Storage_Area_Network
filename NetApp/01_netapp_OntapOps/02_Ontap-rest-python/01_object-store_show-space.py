from netapp_ontap import config, HostConnection
from netapp_ontap.resources import Aggregate
import argparse
import getpass


def get_aggregate_info(host, username, password):
    """Fetch and display available fields for aggregates."""
    try:
        # Connect to ONTAP
        config.CONNECTION = HostConnection(
            host,
            username=username,
            password=password,
            verify=False  # Disable SSL verification
        )

        # Fetch aggregate information
        print("Fetching aggregate details...")
        aggregates = Aggregate.get_collection()

        for aggr in aggregates:
            aggr.get()  # Retrieve all fields for the aggregate
            print(f"Aggregate Name: {aggr.name}")
            print(f"Fields: {aggr.to_dict()}")  # Dump all fields for inspection
            print("-" * 40)

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="ONTAP Aggregate Field Inspector")
    parser.add_argument("host", help="ONTAP hostname or IP address")
    parser.add_argument("username", help="ONTAP username")
    args = parser.parse_args()

    # Securely get password input
    password = getpass.getpass(prompt="Enter your password: ")

    # Call the function
    get_aggregate_info(args.host, args.username, password)

