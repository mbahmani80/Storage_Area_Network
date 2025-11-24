import os
import sys
import json
import subprocess
import mysql.connector
from datetime import datetime
from contextlib import contextmanager
import time  

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project_directory)
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path
sys.path.append(parent_dir)

# Now you can import modules from the mylib package
from mylib import p00_tools_functions
from mylib.p00_tools_functions import c_SystemDBrunFunctions

# Path to JSON files
snapmirror_policies_info_json = os.path.abspath("ymls/json/Display_snapmirror_policies_info.json")
p_book_snapmirror_policies_info = os.path.abspath("ymls/12_Display_snapmirror_policies_info_rest.yml")

def format_elapsed_time(elapsed_time):
    if elapsed_time < 60:
        return f"{elapsed_time:.2f} seconds"
    else:
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        return f"{minutes} minutes and {seconds:.2f} seconds"

class c_ONTAPInfo_SnapMirrorManager:
    def __init__(self):
        self.backup_stg_name = None
        self.customer_id = None
        self.source_path = None
        self.source_vserver = None
        self.source_volume = None
        self.destination_path = None
        self.destination_vserver = None
        self.destination_volume = None
        self.policy = None
        self.lag_time = None
        self.source_path_destination_path = None

    def format_datetime(self, datetime_str):
        try:
            dt_object = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt_object.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Error: Unable to parse datetime string '{datetime_str}'")
            return None

    def extract_info(self, stg_name, customer_id, snapmirror):
        # Load ONTAP info from JSON file
        if not snapmirror:
            print("No JSON data loaded.")
            return 1
        
        # Extracting fields as variables
        self.backup_stg_name = stg_name
        self.customer_id = customer_id
        self.source_path = snapmirror.get('source_path')
        self.source_vserver = snapmirror.get('source_vserver')
        self.source_volume = snapmirror.get('source_volume')
        self.destination_path = snapmirror.get('destination_path')
        self.destination_vserver = snapmirror.get('destination_vserver')
        self.destination_volume = snapmirror.get('destination_volume')
        self.policy = snapmirror.get('policy')
        self.lag_time = snapmirror.get('lag_time')
        
        # Create the composite primary key value
        self.source_path_destination_path = f"{self.source_path}-{self.destination_path}"

    def insert_snapmirror_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            iquery = """INSERT INTO t_snapmirror_info
                                            (
                                             backup_stg_name,
                                             customer_id,
                                             source_path,
                                             source_vserver,
                                             source_volume,
                                             destination_path,
                                             destination_vserver,
                                             destination_volume,
                                             policy,
                                             lag_time,
                                             source_path_destination_path
                                            )
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            ivalues = (
                       self.backup_stg_name,
                       self.customer_id,
                       self.source_path,
                       self.source_vserver,
                       self.source_volume,
                       self.destination_path,
                       self.destination_vserver,
                       self.destination_volume,
                       self.policy,
                       self.lag_time,
                       self.source_path_destination_path
                      )

            cursor.execute(iquery, ivalues)
            conn.commit()
            print("Snapmirror_info: ", "source_path:",self.source_path,"destination_path:", self.destination_path,"policy:", self.policy, " inserted successfully!")
            return True
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return False

    def update_snapmirror_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            uquery = """UPDATE t_snapmirror_info
                        SET
                         backup_stg_name = %s,
                         customer_id = %s,
                         source_path = %s,
                         source_vserver = %s,
                         source_volume = %s,
                         destination_path = %s,
                         destination_vserver = %s,
                         destination_volume = %s,
                         policy = %s,
                         lag_time = %s
                        WHERE source_path_destination_path = %s"""
            uvalues = (
                       self.backup_stg_name,
                       self.customer_id,
                       self.source_path,
                       self.source_vserver,
                       self.source_volume,
                       self.destination_path,
                       self.destination_vserver,
                       self.destination_volume,
                       self.policy,
                       self.lag_time,
                       self.source_path_destination_path
                      )

            cursor.execute(uquery, uvalues)
            conn.commit()
            print("Snapmirror_info: ", "source_path:",self.source_path,"destination_path:", self.destination_path,"policy:", self.policy, " Updated successfully!")
            return True
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return False


    def insert_or_update_snapmirror_info(self, conn, stg_name, customer_id, json_snapmirror_info):
        try:
            cursor = conn.cursor(dictionary=True)
            snapmirror_record = json_snapmirror_info['msg']['records']
            if not json_snapmirror_info['msg']['records']:
                print("No records found in the JSON data. Exiting.")
                return False

            for record in snapmirror_record:
                
                source_path = record.get('source_path')
                destination_path = record.get('destination_path')
                source_path_destination_path = f"{source_path}-{destination_path}"
                self.extract_info(stg_name, customer_id ,record)
                print(f"source_path_destination_path: {source_path_destination_path}")

                cursor.execute("SELECT * FROM t_snapmirror_info WHERE source_path_destination_path = %s", (source_path_destination_path,))
                existing_record = cursor.fetchone()
                if existing_record:
                    # If the record exists, update it
                    print("Record exists, updating...")
                    update_result = self.update_snapmirror_info(conn)
                    if not update_result:
                        return False
                else:
                    # If the record doesn't exist, insert it
                    print("Record does not exist, inserting...")
                    insert_result = self.insert_snapmirror_info(conn)
                    if not insert_result:
                        return False
    
            print("snapmirror information added or updated successfully!")
            return 0  # Success
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return 3  # Return error code 3 for MySQL errors
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return 4  # Return error code 4 for other exceptions

    def print_vars(self):
        print(f"self.backup_stg_name: {self.backup_stg_name}")
        print(f"self.customer_id: {self.customer_id}")
        print(f"self.source_path: {self.source_path}")
        print(f"self.source_vserver: {self.source_vserver}")
        print(f"self.source_volume: {self.source_volume}")
        print(f"self.destination_path: {self.destination_path}")
        print(f"self.destination_vserver: {self.destination_vserver}")
        print(f"self.destination_volume: {self.destination_volume}")
        print(f"self.policy: {self.policy}")
        print(f"self.lag_time: {self.lag_time}")
        print(f"self.source_path_destination_path: {self.source_path_destination_path}")


    
def main():
    try:
        start_time = time.time()  # Record the start time

        sys_db_run = c_SystemDBrunFunctions()
        conn = sys_db_run.connect_to_database()
        if not conn:
            return 5  # Return error code 5 if connection fails

        sys_db_run.delete_json_file(snapmirror_policies_info_json)

        snapmirror_manager = c_ONTAPInfo_SnapMirrorManager()

        sql = "SELECT t_stg_info.stg_name,t_stg_info.stg_uuid,t_stg_info.stg_mgmt_ip,t_stg_info.customer_id FROM t_stg_info JOIN t_stg_access_data ON t_stg_info.stg_mgmt_ip = t_stg_access_data.storageip WHERE t_stg_access_data.enabled = 1"
#    sql = """
#            SELECT
#                t_stg_info.stg_name,
#                t_stg_info.stg_uuid,
#                t_stg_info.stg_mgmt_ip,
#                t_stg_info.customer_id
#            FROM
#                t_stg_info
#            JOIN
#                t_stg_access_data
#            ON
#                t_stg_info.stg_mgmt_ip = t_stg_access_data.storageip
#            WHERE
#                t_stg_access_data.enabled = 1;
#         """

        results_list = sys_db_run.run_sql_query(conn, sql)
        for result in results_list:
            stg_name = result['stg_name']
            customer_id = result['customer_id']
            stg_ip = result['stg_mgmt_ip']
            print(f"Storage Name: {stg_name}, Management IP: {stg_ip}")

            if sys_db_run.check_ip_accessibility(stg_ip):
                # Fetch node information from the JSON file
                status = sys_db_run.run_ansible_playbook2(p_book_snapmirror_policies_info, result['stg_mgmt_ip'],snapmirror_policies_info_json,conn)
                if status:
                    json_snapmirror_info = sys_db_run.load_json(snapmirror_policies_info_json)
    
                    if json_snapmirror_info is None:
                        return 6  # Return error code 6 if JSON loading fails
                    # # Insert or update record in the database
                    result = snapmirror_manager.insert_or_update_snapmirror_info(conn, stg_name, customer_id, json_snapmirror_info)
                    if result != 0:
                        return result  # Return the error code from insert_or_update_aggregate_info
        # Close database connection
        conn.close()

        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        readable_time = format_elapsed_time(elapsed_time)  # Format the elapsed time
        print(f"Script executed in {readable_time}.")  # Print the formatted elapsed time

    except mysql.connector.Error as err:
        print("MySQL Error:", err)

if __name__ == "__main__":
    main()
