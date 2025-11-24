import os
import sys
import json
import mysql.connector
import zipfile
from datetime import datetime, timedelta

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project_directory)
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path
sys.path.append(parent_dir)

# Now you can import modules from the mylib package
from mylib import p00_tools_functions
from mylib.p00_tools_functions import c_SystemDBrunFunctions
from mylib.p00_tools_functions import LogManager
from mylib import p01_add_customer_to_db
from mylib.p01_add_customer_to_db import c_CustomerManager
from mylib import p02_add_datacenters_to_db
from mylib.p02_add_datacenters_to_db import c_DatacenterManager

# Define the files path for c_ONTAPInfo class
json_customer_data_ids_file_path = os.path.abspath("ymls/json/customer_data_ids.json")
json_display_ontap_info_rest = os.path.abspath("ymls/json/Display_ontap_info_rest.json")
json_display_ontap_metrocluster_info_rest = os.path.abspath("ymls/json/Display_ontap_metrocluster_info_rest.json")

p_book_ontap_info = os.path.abspath("ymls/01_Display_ontap_info_rest.yml")
p_book_ontap_metrocluster_info = os.path.abspath("ymls/02_Display_ontap_metrocluster_info_rest.yml")

log_file_path = os.path.abspath("../log/p03_add_ontap_info")

class c_ONTAPInfo:
    def __init__(self, log_file_path):
        self.ontap_info = None
        self.ontap_metrocluster_info = None
        self.stg_name = None
        self.stg_uuid = None
        self.stg_version = None
        self.stg_mgmt_ip = None
        self.stg_timezone = None
        self.local_config_state = None
        self.remote_config_state = None
        self.remote_cluster_name = None
        self.remote_cluster_uuid = None
        self.configuration_type = None
        self.customer_id = None
        self.datacenter_id = None
        self.stgip = None
        # Create an instance of LogManager
        self.log_manager = LogManager(log_file_path)
        # Archive old log files
        self.log_manager.zip_old_logs()

    def extract_info(self, json_ontap_info, json_ontap_metrocluster_info, customer_id, datacenter_id, stgip):
        """Extract necessary information from loaded ONTAP info."""

        # Load ONTAP info from JSON file
        self.ontap_info = json_ontap_info
        if not self.ontap_info:
            print("No JSON data loaded.")
            return 1

        self.ontap_metrocluster_info = json_ontap_metrocluster_info
        if not self.ontap_metrocluster_info:
           print("No JSON data loaded.")
           return 1

        self.customer_id = customer_id
        self.datacenter_id = datacenter_id

        ontap_info = self.ontap_info.get('ontap_info', {})
        cluster_info = ontap_info.get('cluster', {})

        self.stg_name = cluster_info.get('name')
        self.stg_uuid = cluster_info.get('uuid')

        # Extracting version part from the full version string
        full_version = cluster_info.get('version', {}).get('full', '')
        version_parts = full_version.split(' ')[2:]
        version_string = ' '.join(version_parts)
        self.stg_version = version_string.split(':')[0] if ':' in version_string else version_string

        self.stg_mgmt_ip = cluster_info.get('management_interfaces', [{}])[0].get('ip', {}).get('address')
        self.stg_timezone = cluster_info.get('timezone', {}).get('name')

        # Extract relevant information

        ontap_metro_info = self.ontap_metrocluster_info.get('ontap_info', {}).get('cluster/metrocluster', {})
        self.local_config_state = ontap_metro_info['local'].get('configuration_state')
        if 'remote' in ontap_metro_info:
            self.remote_config_state = ontap_metro_info['remote'].get('configuration_state')
            self.remote_cluster_name = ontap_metro_info['remote']['cluster'].get('name')
            self.remote_cluster_uuid = ontap_metro_info['remote']['cluster'].get('uuid')
        else:
            self.remote_config_state = None
            self.remote_cluster_name = None
            self.remote_cluster_uuid = None

        self.configuration_type = ontap_metro_info.get('configuration_type')
        self.stgip = stgip
        return 0

    def print_new_record(self):
        """Print the newly inserted record."""
        if not self.ontap_info:
            message = (
                f"\n"
                f"No ONTAP info available to print.\n"
                f"------------------\n"
            )
            print(message)
            self.log_manager.update_log(message)
            return

        # Check if all required keys are present
        if any(field is None for field in [self.stg_name, self.stg_uuid, self.stg_version, self.stg_mgmt_ip, self.stg_timezone]):
            message = (
                f"\n"
                f"Error: Missing required keys in ONTAP info.\n"
                f"------------------\n"
            )
            print(message)
            self.log_manager.update_log(message)
            return

        # Create the message string with all the details
        message = (
            f"\n"
            f"stg_name: {self.stg_name}\n"
            f"stg_uuid: {self.stg_uuid}\n"
            f"stg_version: {self.stg_version}\n"
            f"stg_mgmt_ip: {self.stg_mgmt_ip}\n"
            f"stg_timezone: {self.stg_timezone}\n"
            f"Metro Cluster Local config state: {self.local_config_state}\n"
            f"------------------\n"
        )
        # Log the message
        self.log_manager.update_log(message)
        print(message) 


    # Function to write customer_id and datacenter_id to a JSON file
    def write_ids_to_json(self,customer_id, datacenter_id, file_path):
        ids = {
            "customer_id": customer_id,
            "datacenter_id": datacenter_id
        }

        try:
            with open(file_path, "w") as json_file:
                json.dump(ids, json_file)
            return 0
        except IOError as e:
            print(f"Error writing to JSON file: {e}")
            return 1

    # Function to handle the insertion or update of ONTAP info
    def insert_update_stg_info(self, conn):
        if self.record_exists(conn):
            self.update_stg_info(conn)
        else:
            self.insert_stg_info(conn)

    # Function to handle the insertion or update of ONTAP info with exception handling
    def insert_update_stg_info(self, conn):
        try:
            if self.record_exists(conn):
                self.update_stg_info(conn)
            else:
                self.insert_stg_info(conn)
        except mysql.connector.Error as err:
            print(f"Error in insert/update operation: {err}")
            return 1
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return 1
        else:
            print("Operation completed successfully.")
            return 0

    # Function to check if the record already exists in the database
    def record_exists(self, conn):
        # Load ONTAP info from JSON file
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM t_stg_info WHERE stg_uuid = %s", (self.stg_uuid,))
        return cursor.fetchone()

    # Function to check if the record already exists in the database
    def record_exists2(self, conn, json_ontap_info):
        # Load ONTAP info from JSON file
        self.ontap_info = json_ontap_info
        if not self.ontap_info:
            print("No JSON data loaded.")
            return 1

        ontap_info = self.ontap_info.get('ontap_info', {})
        cluster_info = ontap_info.get('cluster', {})
        self.stg_uuid = cluster_info.get('uuid')

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM t_stg_info WHERE stg_uuid = %s", (self.stg_uuid,))
        return cursor.fetchone()

    # Function to check if the record already exists in the database
    def record_exists3(self, conn):
        cursor = conn.cursor(dictionary=True)

        # Execute the SQL query
        cursor.execute("SELECT stg_name, stg_uuid, stg_mgmt_ip FROM t_stg_info")
        return cursor.fetchall() 

    # Function to update the existing record
    def update_stg_info(self, conn):
        try:



            usql = """UPDATE t_stg_info
                      SET stg_name=%s, stg_version=%s, stg_mgmt_ip=%s, stg_timezone=%s,
                          metrocluster_local_configuration_state=%s, metrocluster_remote_configuration_state=%s,
                          metrocluster_remote_cluster_name=%s, metrocluster_remote_cluster_uuid=%s,
                          metrocluster_configuration_type=%s
                      WHERE stg_uuid=%s AND customer_id=%s AND datacenter_id=%s"""
            uvalues = (self.stg_name, self.stg_version, self.stg_mgmt_ip, self.stg_timezone,
                       self.local_config_state, self.remote_config_state, self.remote_cluster_name,
                       self.remote_cluster_uuid, self.configuration_type, self.stg_uuid,
                       self.customer_id, self.datacenter_id)

            cursor = conn.cursor()
            cursor.execute(usql, uvalues)
            conn.commit()
            self.print_new_record()
            print("ONTAP info updated successfully.")
            return 0
        except mysql.connector.Error as err:
            print(f"Error updating ONTAP info: {err}")
            return 1

    # Function to insert a new record
    def insert_stg_info(self, conn):
        try:
            isql = """INSERT INTO t_stg_info
                      (stg_name, stg_uuid, stg_version, stg_mgmt_ip, stg_timezone, customer_id, datacenter_id,
                       metrocluster_local_configuration_state, metrocluster_remote_configuration_state,
                       metrocluster_remote_cluster_name, metrocluster_remote_cluster_uuid,
                       metrocluster_configuration_type)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            ivalues = (self.stg_name, self.stg_uuid, self.stg_version, self.stg_mgmt_ip, self.stg_timezone,
                       self.customer_id, self.datacenter_id, self.local_config_state, self.remote_config_state,
                       self.remote_cluster_name, self.remote_cluster_uuid, self.configuration_type)

            cursor = conn.cursor()
            cursor.execute(isql, ivalues)
            conn.commit()
            print("New Record Inserted:")
            self.print_new_record()
            return 0
        except mysql.connector.Error as err:
            print(f"Error inserting ONTAP info: {err}")
            return 1


    # Function to delete records not found in the JSON file
    def delete_unmatched_records(self, conn, json_data, stgip):

        # Extract the UUID from the JSON data
        json_uuids = {json_data['ontap_info']['cluster']['uuid']}

        cursor = conn.cursor()
        # Fetch all UUIDs from the database
        cursor.execute(f"SELECT stg_uuid FROM t_stg_info WHERE stg_mgmt_ip = %s", (stgip,))
        db_uuids = {row[0] for row in cursor.fetchall()}

        # Find UUIDs that are in the database but not in the JSON file
        unmatched_uuids = db_uuids - json_uuids

        # Delete these records from the database
        for uuid in unmatched_uuids:
            cursor.execute(f"DELETE FROM t_stg_info WHERE stg_uuid = %s", (uuid,))
        conn.commit()
        cursor.close()
        print(f"Deleted {len(unmatched_uuids)} records from t_stg_info.")



# Main function
def main():

    # Connect to the database
    sys_db_run = c_SystemDBrunFunctions()
    # Connect to the MariaDB database
    conn = sys_db_run.connect_to_database()
    if not conn:
        return 1  # Return error code 1 if connection fails
    #stgip="192.168.56.4"
    # Create CustomerManager instance
    customer_manager = c_CustomerManager(conn)
    dc_manager = c_DatacenterManager(conn, customer_manager)


    sys_db_run.delete_json_file(json_display_ontap_info_rest)
    sys_db_run.delete_json_file(json_display_ontap_metrocluster_info_rest)

    valid_ips = sys_db_run.process_ips()
    for stgip in valid_ips:
        if sys_db_run.check_ip_accessibility(stgip):
            status1 = sys_db_run.run_ansible_playbook2(p_book_ontap_info,stgip, json_display_ontap_info_rest, conn)
            status2 = sys_db_run.run_ansible_playbook2(p_book_ontap_metrocluster_info, stgip, json_display_ontap_metrocluster_info_rest, conn)
            if status1 and status2:
                # Create c_ONTAPInfo instance
                json_ontap_info = sys_db_run.load_json(json_display_ontap_info_rest)
                json_ontap_metrocluster_info = sys_db_run.load_json(json_display_ontap_metrocluster_info_rest)
                ontap_info = c_ONTAPInfo(log_file_path)
    
                # Get customer and datacenter choice
                # Fetch the result
                result = ontap_info.record_exists2(conn,json_ontap_info)
    
                # Check if we got a result
                if result:
                    customer_id = result['customer_id']
                    datacenter_id = result['datacenter_id']
                    print(f"customer_id: {customer_id}, datacenter_id: {datacenter_id}")
                else:
                    print("No records found.")
                    selected_datacenter = dc_manager.show_datacenter_and_select()
                    if selected_datacenter:
                        print("------------------------")
                        print(selected_datacenter)
                        print("------------------------")
                        datacenter_id = selected_datacenter[0]
                        customer_id   = selected_datacenter[5]
                        print("Chosen customer ID:", customer_id)
                        print("Chosen datacenter ID:", datacenter_id)
        
                # Insert ONTAP info into t_stg_info table
                result_extract_info = ontap_info.extract_info(json_ontap_info, json_ontap_metrocluster_info, customer_id, datacenter_id, stgip)
                if result_extract_info != 0:
                    return result_extract_info
                else:
                    result_update_insert = ontap_info.insert_update_stg_info(conn)
                    if result_update_insert != 0:
                        return result_update_insert
                    else:
                        # Write customer_id and datacenter_id to a JSON file
                        result_write = ontap_info.write_ids_to_json(customer_id, datacenter_id, json_customer_data_ids_file_path)
                        if result_write != 0:
                            return result_write
    
                ontap_info.delete_unmatched_records(conn, json_ontap_info, stgip)
        else:
            print("Add Storage username, pass, ... into db. Run p198_insert_stg_login_data_to_db.py")
    # Close database connection
    conn.close()
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
