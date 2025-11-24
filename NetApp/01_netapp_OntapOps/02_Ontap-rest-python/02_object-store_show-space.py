from netapp_ontap import config, HostConnection
from netapp_ontap.resources import Aggregate
import argparse
import getpass


def fetch_object_store_space(host, username, password):
    """Fetch and display object-store space details for each aggregate."""
    try:
        # Connect to ONTAP
        config.CONNECTION = HostConnection(
            host,
            username=username,
            password=password,
            verify=False  # Disable SSL verification
        )

        # Fetch aggregate information
        print("Fetching object-store space details...\n")
        aggregates = Aggregate.get_collection()

        for aggr in aggregates:
            aggr.get()  # Retrieve full details of the aggregate
            print(f"Aggregate Name: {aggr.name}")

            # Extract cloud storage details
            if aggr.cloud_storage and aggr.cloud_storage.get("stores"):
                for store in aggr.cloud_storage["stores"]:
                    cloud_store_link = store["cloud_store"]["_links"]["self"]["href"]
                    used_space = store.get("used", "N/A")
                    print(f"  Cloud Store Link: {cloud_store_link}")
                    print(f"  Used Space: {used_space} bytes")
            else:
                print("  No cloud storage attached to this aggregate.")

            print("-" * 40)

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="ONTAP Object-Store Space Inspector")
    parser.add_argument("host", help="ONTAP hostname or IP address")
    parser.add_argument("username", help="ONTAP username")
    args = parser.parse_args()

    # Securely get password input
    password = getpass.getpass(prompt="Enter your password: ")

    # Call the function
    fetch_object_store_space(args.host, args.username, password)

