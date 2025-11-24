from netapp_ontap import config, HostConnection
from netapp_ontap.resources import Cluster
import argparse
import getpass


def fetch_cluster_info(host, username, password):
    """Fetch and display specified cluster information."""
    try:
        # Connect to ONTAP
        config.CONNECTION = HostConnection(
            host,
            username=username,
            password=password,
            verify=False  # Disable SSL verification
        )

        # Fetch cluster information
        print("Fetching cluster information...\n")
        cluster = Cluster.get()

        # Display cluster details
        print(f"Cluster Name: {cluster.name}")
        print(f"Cluster UUID: {cluster.uuid}")
        print(f"Cluster Version: {cluster.version.full}")

        # Management Interfaces
        management_interfaces = cluster.management_interfaces
        if management_interfaces:
            for interface in management_interfaces:
                ip_address = interface.ip.address if interface.ip else "N/A"
                print(f"Management Interface IP Address: {ip_address}")
        else:
            print("No management interfaces found.")

        # Timezone Information
        print(f"Cluster Timezone: {cluster.timezone.name}")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch ONTAP Cluster Information")
    parser.add_argument("host", help="ONTAP hostname or IP address")
    parser.add_argument("username", help="ONTAP username")
    args = parser.parse_args()

    # Securely get password input
    password = getpass.getpass(prompt="Enter your password: ")

    # Call the function to fetch and display cluster information
    fetch_cluster_info(args.host, args.username, password)

