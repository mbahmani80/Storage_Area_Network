import os
import sys
import mysql.connector
from mysql.connector import Error
import getpass
import subprocess
import yaml

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project_directory)
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path
sys.path.append(parent_dir)

# Import modules from the mylib package
from mylib import p00_tools_functions
from mylib.p00_tools_functions import c_SystemDBrunFunctions

vault_password_file='/home/ubuntu/01_lab/vault_password_file'

class c_OntapLoginData:
    def __init__(self, vault_password_file):
        self.vault_password_file = vault_password_file

    def fetch_customers(self, conn):
        """Fetch customer details from the database."""
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT customer_id, customer_name FROM t_customer ORDER BY customer_id")
            customers = cursor.fetchall()
            cursor.close()
            return customers
        except Error as e:
            print("Error while fetching customer data", e)
            return []

    def display_customers(self, customers):
        """Display customer information."""
        print("\nAvailable customers:")
        for customer in customers:
            print(f"ID: {customer['customer_id']}, Name: {customer['customer_name']}")

    def encrypt_password(self, password):
        """Encrypt the password using ansible-vault and return the encrypted string."""
        try:
            process = subprocess.run(
                ['ansible-vault', 'encrypt_string', password, '--vault-password-file', self.vault_password_file, '--encrypt-vault-id', 'default', '--name', 'password'],
                capture_output=True, text=True, check=True
            )
            # Extract the encrypted value from the output
            encrypted_value = process.stdout.strip().split('\n', 1)[1].strip()
            return encrypted_value
        except subprocess.CalledProcessError as e:
            print(f"Error encrypting password: {e}")
            return None

    def get_user_input(self, conn):
        """Prompt the user for input and return a dictionary with the data."""
        customers = self.fetch_customers(conn)
        self.display_customers(customers)

        storageip = input("Enter storage IP: ")
        storagename = input("Enter storage name: ")
        username = input(f"Enter username [admin]: ") or 'admin'
        password = getpass.getpass("Enter password: ")  # Securely get the password
        https = input("Enable HTTPS (yes/no) [yes]: ").strip().lower() or 'yes'
        validate_certs = input("Validate certificates (yes/no) [no]: ").strip().lower() or 'no'
        configtype = input("Enter config type (MetroCluster, MirrorCluster, Ontapselect, BackupCluster) [MetroCluster]: ").strip() or 'MetroCluster'
        enabled = input("Enable (yes/no) [yes]: ").strip().lower() or 'yes'

        customer_id = input("Enter customer ID (or press Enter to skip): ")
        customer_id = int(customer_id) if customer_id else None

        # Encrypt the password before storing it
        encrypted_password = self.encrypt_password(password)

        return {
            'storageip': storageip,
            'storagename': storagename,
            'username': username,
            'password': encrypted_password,
            'https': https == 'yes',
            'validate_certs': validate_certs == 'yes',
            'configtype': configtype,
            'enabled': enabled == 'yes',
            'customer_id': customer_id
        }

    def insert_data(self, conn, data):
        """Insert or update a record in the t_stg_access_data table."""
        try:
            cursor = conn.cursor()

            # SQL statement to insert data
            insert_query = """
            INSERT INTO t_stg_access_data
            (storageip, storagename, username, password, https, validate_certs, configtype, enabled, customer_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            username=VALUES(username),
            password=VALUES(password),
            https=VALUES(https),
            validate_certs=VALUES(validate_certs),
            configtype=VALUES(configtype),
            enabled=VALUES(enabled),
            customer_id=VALUES(customer_id);
            """

            # Insert data
            cursor.execute(insert_query, (
                data.get('storageip'),
                data.get('storagename'),
                data.get('username'),
                data.get('password'),
                data.get('https'),
                data.get('validate_certs'),
                data.get('configtype'),
                data.get('enabled'),
                data.get('customer_id')
            ))

            conn.commit()
            print(f"Record inserted/updated successfully into t_stg_access_data table")

        except Error as e:
            print("Error while inserting data into MySQL", e)
        finally:
            if conn.is_connected():
                cursor.close()

    def update_storage_status(self, conn, ips, enable=True):
        """Update the enabled status of storage based on the provided IPs."""
        try:
            status = 1 if enable else 0  # Set status to 1 for enable and 0 for disable
            cursor = conn.cursor()

            ip_list = ips.split(',')
            formatted_ips = ', '.join(['%s'] * len(ip_list))

            update_query = f"""
            UPDATE t_stg_access_data
            SET enabled = %s
            WHERE storageip IN ({formatted_ips});
            """

            cursor.execute(update_query, (status, *ip_list))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"Storage with IPs {', '.join(ip_list)} {'enabled' if enable else 'disabled'} successfully.")
            else:
                print(f"No storage found with the provided IPs: {', '.join(ip_list)}.")

        except Error as e:
            print(f"Error while {'enabling' if enable else 'disabling'} storage in MySQL", e)
        finally:
            if conn.is_connected():
                cursor.close()

    def update_All_storage_status(self, conn, enable=True):
        """Update the enabled status of storage based on the provided IPs."""
        try:
            status = 1 if enable else 0  # Set status to 1 for enable and 0 for disable
            cursor = conn.cursor()

            update_query = f"""
            UPDATE t_stg_access_data
            SET enabled = %s;
            """

            cursor.execute(update_query, (status,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"All Storage  {'enabled' if enable else 'disabled'} successfully.")
            else:
                print(f"No storage found.")

        except Error as e:
            print(f"Error while {'enabling' if enable else 'disabling'} storage in MySQL", e)
        finally:
            if conn.is_connected():
                cursor.close()

    def show_storage(self, conn):
        """Show storage information."""
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT s.storageip, s.storagename, s.configtype, s.enabled, s.customer_id, c.customer_name
            FROM t_stg_access_data s
            LEFT JOIN t_customer c ON s.customer_id = c.customer_id
            ORDER BY s.customer_id;
            """
            cursor.execute(query)
            storages = cursor.fetchall()
            cursor.close()

            print("\nStorage Information:")
            for storage in storages:
                print(f"ID: {storage['customer_id']}, Customer: {storage['customer_name']}, "
                f"STG_IP: {storage['storageip']}, STG_Name: {storage['storagename']}, Enabled: {storage['enabled']}, configtype: {storage['configtype']}")
                print("---------------------------------------------------------------")
        except Error as e:
            print("Error while fetching storage data", e)

    def delete_storage(self, conn, ips):
        """Delete storage records based on the provided IPs."""
        try:
            cursor = conn.cursor()

            ip_list = ips.split(',')
            formatted_ips = ', '.join(['%s'] * len(ip_list))

            delete_query = f"""
            DELETE FROM t_stg_access_data
            WHERE storageip IN ({formatted_ips});
            """

            cursor.execute(delete_query, ip_list)
            conn.commit()

            if cursor.rowcount > 0:
                print(f"Storage with IPs {', '.join(ip_list)} deleted successfully.")
            else:
                print(f"No storage found with the provided IPs: {', '.join(ip_list)}.")

        except Error as e:
            print(f"Error while deleting storage from MySQL", e)
        finally:
            if conn.is_connected():
                cursor.close()

    def show_menu(self):
        """Display the menu options."""
        print("\nMenu:")
        print("1. Show storage data")
        print("2. Insert or update storage data")
        print("3. Enable storage")
        print("4. Disable storage")
        print("5. Enable All storage")
        print("6. Disable All storage")
        print("7. Delete storage")
        print("x. Exit")

def main():
    # Instantiate the c_SystemDBrunFunctions class 
    sys_db_run = c_SystemDBrunFunctions()
    # Connect to the MariaDB database
    conn = sys_db_run.connect_to_database()
    if not conn:
        return 1  # Return error code 1 if conn fails

    db_manager = c_OntapLoginData(vault_password_file)  # Instantiate the class

    if conn:
        while True:
            db_manager.show_menu()
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                db_manager.show_storage(conn)
            elif choice == '2':
                data = db_manager.get_user_input(conn)
                db_manager.insert_data(conn, data)
            elif choice == '3':
                db_manager.show_storage(conn)
                ips = input("Enter comma-separated storage IPs to enable: ").strip()
                db_manager.update_storage_status(conn, ips, enable=True)
            elif choice == '4':
                db_manager.show_storage(conn)
                ips = input("Enter comma-separated storage IPs to disable: ").strip()
                db_manager.update_storage_status(conn, ips, enable=False)
            elif choice == '5':
                db_manager.update_All_storage_status(conn, enable=True)
                db_manager.show_storage(conn)
            elif choice == '6':
                db_manager.update_All_storage_status(conn, enable=False)
                db_manager.show_storage(conn)
            elif choice == '7':
                db_manager.show_storage(conn)
                ips = input("Enter comma-separated storage IPs to delete login infos: ").strip()
                db_manager.delete_storage(conn, ips)
            elif choice == 'x':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please try again.")

        conn.close()

if __name__ == "__main__":
    main()
