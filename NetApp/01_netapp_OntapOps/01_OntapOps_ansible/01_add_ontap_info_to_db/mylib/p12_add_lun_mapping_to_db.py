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
json_lun_mapping_info = os.path.abspath("ymls/json/Display_lun_mapping_info.json")
p_book_lun_mapping_info = os.path.abspath("ymls/13_Display_lun_mapping_info_rest.yml")

def format_elapsed_time(elapsed_time):
    if elapsed_time < 60:
        return f"{elapsed_time:.2f} seconds"
    else:
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        return f"{minutes} minutes and {seconds:.2f} seconds"

class c_ONTAPInfo_LUN_Mapping:
    def __init__(self):
        self.vserver = None
        self.path = None
        self.volume = None
        self.lun = None
        self.igroup = None
        self.ostype = None
        self.protocol = None
        self.lun_id = None
        self.initiators = None
        self.lun_igroup = None

    def format_datetime(self, datetime_str):
        try:
            dt_object = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt_object.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Error: Unable to parse datetime string '{datetime_str}'")
            return None

    def extract_info(self, stg_name, lunmapping):
        # Load ONTAP info from JSON file
        if not lunmapping:
            print("No JSON data loaded.")
            return 1
        
        # Extracting fields as variables
        self.stg_name = stg_name
        self.vserver =  lunmapping.get('vserver')
        self.path = lunmapping.get('path')
        self.volume = lunmapping.get('volume')
        self.lun = lunmapping.get('lun')
        self.igroup = lunmapping.get('igroup')
        self.ostype = lunmapping.get('ostype')
        self.protocol = lunmapping.get('protocol')
        self.lun_id = lunmapping.get('lun_id')
        self.initiators = ','.join(lunmapping.get('initiators', []))
        # Create the composite primary key value
        self.lun_igroup = f"{self.lun}-{self.igroup}"

    def insert_lunmapping_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            iquery = """INSERT INTO  t_lun_mapping
                                            (
                                             stg_name,
                                             vserver,
                                             path,
                                             volume,
                                             lun,
                                             igroup,
                                             ostype,
                                             protocol,
                                             lun_id,
                                             initiators,
                                             lun_igroup
                                            )
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            ivalues = (
                       self.stg_name, 
                       self.vserver, 
                       self.path, 
                       self.volume, 
                       self.lun, 
                       self.igroup, 
                       self.ostype, 
                       self.protocol, 
                       self.lun_id, 
                       self.initiators, 
                       self.lun_igroup
                      )

            cursor.execute(iquery, ivalues)
            conn.commit()
            print("lunmapping_info: ", "stg_name:",self.stg_name,"path", self.path,"igroup:", self.igroup,"initiators", self.initiators," inserted successfully!")
            return True
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return False

    def update_lunmapping_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            uquery = """UPDATE  t_lun_mapping 
                        SET
                         stg_name = %s,
                         vserver = %s,
                         path = %s,
                         volume = %s,
                         lun = %s,
                         igroup = %s,
                         ostype = %s,
                         protocol = %s,
                         lun_id = %s,
                         initiators = %s
                        WHERE lun_igroup = %s"""
            uvalues = (
                       self.stg_name, 
                       self.vserver, 
                       self.path, 
                       self.volume, 
                       self.lun, 
                       self.igroup, 
                       self.ostype, 
                       self.protocol, 
                       self.lun_id, 
                       self.initiators, 
                       self.lun_igroup
                      )

            cursor.execute(uquery, uvalues)
            conn.commit()
            print("lunmapping_info: ", "stg_name:",self.stg_name,"path", self.path,"igroup:", self.igroup,"initiators", self.initiators," update successfully!")
            return True
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return False


    def insert_or_update_lunmapping_info(self, conn, stg_name, json_lunmapping_info):
        try:
            cursor = conn.cursor(dictionary=True)
            lunmapping_record = json_lunmapping_info['msg']['records']
            if not json_lunmapping_info['msg']['records']:
                print("No records found in the JSON data. Exiting.")
                return False

            for record in lunmapping_record:
                
                lun = record.get('lun')
                igroup = record.get('igroup')
                # Create the composite primary key value
                lun_igroup = f"{lun}-{igroup}"
                self.extract_info(stg_name, record)
                cursor.execute("SELECT * FROM  t_lun_mapping WHERE lun_igroup = %s", (lun_igroup,))
                existing_record = cursor.fetchone()
                self.print_vars()
                if existing_record:
                    # If the record exists, update it
                    print("Record exists, updating...")
                    update_result = self.update_lunmapping_info(conn)
                    if not update_result:
                        return False
                else:
                    # If the record doesn't exist, insert it
                    print("Record does not exist, inserting...")
                    insert_result = self.insert_lunmapping_info(conn)
                    if not insert_result:
                        return False
    
            print("lunmapping information added or updated successfully!")
            return 0  # Success
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return 3  # Return error code 3 for MySQL errors
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return 4  # Return error code 4 for other exceptions

    def print_vars(self):
        print(f"self.stg_name: {self.stg_name}")
        print(f"self.vserver: {self.vserver}")
        print(f"self.path: {self.path}")
        print(f"self.volume: {self.volume}")
        print(f"self.lun: {self.lun}")
        print(f"self.igroup: {self.igroup}")
        print(f"self.ostype: {self.ostype}")
        print(f"self.protocol: {self.protocol}")
        print(f"self.lun_id: {self.lun_id}")
        print(f"self.initiators: {self.initiators}")
        print(f"self.lun_igroup: {self.lun_igroup}")


    
def main():
    try:
        start_time = time.time()  # Record the start time

        sys_db_run = c_SystemDBrunFunctions()
        conn = sys_db_run.connect_to_database()
        if not conn:
            return 5  # Return error code 5 if connection fails

        sys_db_run.delete_json_file(json_lun_mapping_info)

        lunmapping_manager = c_ONTAPInfo_LUN_Mapping()

        sql = "SELECT t_stg_info.stg_name,t_stg_info.stg_uuid,t_stg_info.stg_mgmt_ip FROM t_stg_info JOIN t_stg_access_data ON t_stg_info.stg_mgmt_ip = t_stg_access_data.storageip WHERE t_stg_access_data.enabled = 1"
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
            stg_ip = result['stg_mgmt_ip']
            print(f"Storage Name: {stg_name}, Management IP: {stg_ip}")

            if sys_db_run.check_ip_accessibility(stg_ip):
                # Fetch node information from the JSON file
                status = sys_db_run.run_ansible_playbook2(p_book_lun_mapping_info, result['stg_mgmt_ip'],json_lun_mapping_info,conn)
                if status:
                    json_lunmapping_info = sys_db_run.load_json(json_lun_mapping_info)
    
                    if json_lunmapping_info is None:
                        return 6  # Return error code 6 if JSON loading fails
                    # Insert or update record in the database
                    result = lunmapping_manager.insert_or_update_lunmapping_info(conn, stg_name, json_lunmapping_info)
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
