import os
import sys
import json
import mysql.connector

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project_directory)
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path
sys.path.append(parent_dir)

# Now you can import modules from the mylib package
from mylib import p00_tools_functions
from mylib.p00_tools_functions import c_SystemDBrunFunctions

# Define the files path
json_display_aggregates_info_rest = os.path.abspath("ymls/json/Display_aggregates_info_rest.json")
p_book_aggregates_info = os.path.abspath("ymls/05_Display_aggregates_info_rest.yml")

class c_ONTAPInfo_Aggregate:
    def __init__(self):
        self.aggr_name = None 
        self.aggr_uuid = None
        self.aggr_state = None
        self.aggr_available_space = None
        self.aggr_total_size = None
        self.aggr_used_space = None
        self.aggr_storage_type = None
        self.aggr_vol_count = None
        self.aggr_node_name = None
        self.aggr_node_uuid = None

    def extract_info(self, record):
        # Load ONTAP info from JSON file
        if not record:
            print("No JSON data loaded.")
            return 1
        self.aggr_name = record.get('name')
        self.aggr_uuid = record.get('uuid')
        self.aggr_state = record.get('state')
        self.aggr_available_space = str((record.get('space', {}).get('block_storage', {}).get('available')) / 1024 / 1024 / 1024)
        self.aggr_total_size = str((record.get('space', {}).get('block_storage', {}).get('size')) / 1024 / 1024 / 1024)
        self.aggr_used_space = str((record.get('space', {}).get('block_storage', {}).get('used')) / 1024 / 1024 / 1024)
        #aggr_available_space = record.get('space', {}).get('block_storage', {}).get('available')
        #aggr_total_size = record.get('space', {}).get('block_storage', {}).get('size')
        #aggr_used_space = record.get('space', {}).get('block_storage', {}).get('used')
        self.aggr_storage_type = record.get('block_storage', {}).get('storage_type')
        self.aggr_vol_count = record.get('volume_count')
        self.aggr_node_name = record.get('node', {}).get('name')
        self.aggr_node_uuid = record.get('node', {}).get('uuid')


    def insert_aggregate_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            iquery = """INSERT INTO t_aggregates 
                                    (
                                     aggr_name, 
                                     aggr_uuid, 
                                     aggr_state, 
                                     aggr_available_space, 
                                     aggr_total_size, 
                                     aggr_used_space, 
                                     aggr_storage_type, 
                                     aggr_vol_count, 
                                     aggr_node_name, 
                                     aggr_node_uuid) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
            ivalues = (
                       self.aggr_name, 
                       self.aggr_uuid, 
                       self.aggr_state, 
                       self.aggr_available_space, 
                       self.aggr_total_size, 
                       self.aggr_used_space, 
                       self.aggr_storage_type, 
                       self.aggr_vol_count, 
                       self.aggr_node_name, 
                       self.aggr_node_uuid
            )
    
            cursor.execute(iquery, ivalues) 
            conn.commit()
            print("Aggregate Name: ", self.aggr_name)
            print("Aggregate UUID: ", self.aggr_uuid)
            print("Aggregate information inserted successfully.")
            return True
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return False
    
    def update_aggregate_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            uquery = """UPDATE t_aggregates 
                        SET aggr_name = %s, 
                            aggr_state = %s, 
                            aggr_available_space = %s, 
                            aggr_total_size = %s, 
                            aggr_used_space = %s, 
                            aggr_storage_type = %s, 
                            aggr_vol_count = %s, 
                            aggr_node_name = %s 
                        WHERE aggr_node_uuid = %s"""
    
            uvalues = (
                       self.aggr_name, 
                       self.aggr_state, 
                       self.aggr_available_space, 
                       self.aggr_total_size, 
                       self.aggr_used_space, 
                       self.aggr_storage_type, 
                       self.aggr_vol_count, 
                       self.aggr_node_name, 
                       self.aggr_node_uuid
            )
            cursor.execute(uquery, uvalues) 
            conn.commit()
            print("Aggregate Name: ", self.aggr_name)
            print("Aggregate UUID: ", self.aggr_uuid)
            print("Aggregate information updated successfully.")
            return True
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return False

    def insert_or_update_aggregate_info(self, conn, aggregate_info):
        try:
            node_aggregate_info = aggregate_info.get('ontap_info', {}).get('storage/aggregates', {}).get('records', [])
            cursor = conn.cursor()
            for record in node_aggregate_info:
                self.extract_info(record)    
                aggr_uuid = record.get('uuid')
                cursor.execute("SELECT * FROM t_aggregates WHERE aggr_uuid = %s", (aggr_uuid,))
                existing_record = cursor.fetchone()
                if existing_record:
                    update_result = self.update_aggregate_info(conn)
                    if not update_result:
                        return 1  # Return error code 1 if update fails
                else:
                    insert_result = self.insert_aggregate_info(conn)
                    if not insert_result:
                        return 2  # Return error code 2 if insert fails
            return 0  # Success
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return 3  # Return error code 3 for MySQL errors
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return 4  # Return error code 4 for other exceptions

def main():
    try:
        # Connect to the MariaDB database
        sys_db_run = c_SystemDBrunFunctions()
        conn = sys_db_run.connect_to_database()
        if not conn:
            return 5  # Return error code 5 if connection fails

        sys_db_run.delete_json_file(json_display_aggregates_info_rest)
       
        # Create an instance of c_ONTAPInfo_node
        ontap_aggregate_info_handler = c_ONTAPInfo_Aggregate()

        # Print each field from the query
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

        results_list = sys_db_run.run_sql_query(conn,sql)
        for result in results_list:
            print(f"Storage Name: {result['stg_name']}, UUID: {result['stg_uuid']}, Management IP: {result['stg_mgmt_ip']}")
            
            if sys_db_run.check_ip_accessibility(result['stg_mgmt_ip']):
                # Fetch node information from the JSON file
                status = sys_db_run.run_ansible_playbook2(p_book_aggregates_info,result['stg_mgmt_ip'],json_display_aggregates_info_rest,conn)
                if status:
                    json_aggregate_info = sys_db_run.load_json(json_display_aggregates_info_rest)

                    if json_aggregate_info is None:
                        return 6  # Return error code 6 if JSON loading fails
    
                    # Insert or update aggregate information into t_aggregates table
                    result = ontap_aggregate_info_handler.insert_or_update_aggregate_info(conn, json_aggregate_info)
                    if result != 0:
                        return result  # Return the error code from insert_or_update_aggregate_info

        # Close database connection
        conn.close()
        return 0  # Success
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return 7  # Return error code 7 for MySQL connection errors
    except Exception as e:
        print("Error:", e)
        return 8  # Return error code 8 for other exceptions

if __name__ == "__main__":
    sys.exit(main())

