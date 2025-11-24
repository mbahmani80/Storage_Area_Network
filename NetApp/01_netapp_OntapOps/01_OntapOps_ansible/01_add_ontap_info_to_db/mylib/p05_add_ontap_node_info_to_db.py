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
json_display_ontap_node_info_rest = os.path.abspath("ymls/json/Display_ontap_node_info_rest.json")
json_display_ontap_node_info_rest1 = os.path.abspath("ymls/json/Display_ontap_node_info_rest.json1")
json_display_ontap_node_info_rest2 = os.path.abspath("ymls/json/Display_ontap_node_info_rest.json2")

p_book_ontap_node_info = os.path.abspath("ymls/04_Display_ontap_node_info_rest.yml")

class c_ONTAPInfo_node:
    def __init__(self):
        self.node_name = None 
        self.node_uuid = None 
        self.node_model = None 
        self.node_serial_number = None 
        self.node_system_id = None
        self.node_storage_configuration = None 
        self.node_location = None 
        self.node_version = None 
        self.stg_uuid = None 
        self.customer_id = None 
        self.datacenter_id = None
        self.node_mgmt_lif = None  
        self.node_service_processor = None

    def extract_info(self, node_data, mgmt_ip, sp_ip, stg_uuid, customer_id, datacenter_id):
        # Load ONTAP info from JSON file
        if not node_data:
            print("No JSON data loaded.")
            return 1
        self.node_name = node_data.get('name')
        self.node_uuid = node_data.get('uuid')
        self.node_model = node_data.get('model')
        self.node_serial_number = node_data.get('serial_number')
        self.node_system_id = node_data.get('system_id')
        self.node_storage_configuration = node_data.get('storage_configuration')
        self.node_location = node_data.get('location')
        self.node_version = node_data.get('version', {}).get('full')
        self.stg_uuid = stg_uuid 
        self.customer_id = customer_id
        self.datacenter_id = datacenter_id
        self.node_mgmt_lif = mgmt_ip
        self.node_service_processor = sp_ip

    def update_ontap_node_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            uquery = """UPDATE t_stg_node_info 
                        SET node_name=%s, 
                            node_model=%s, 
                            node_serial_number=%s,
                            node_system_id=%s, 
                            node_storage_configuration=%s, 
                            node_location=%s, 
                            node_version=%s,
                            stg_uuid=%s, 
                            customer_id=%s, 
                            datacenter_id=%s,
                            node_mgmt_lif=%s,
                            node_service_processor=%s 
                        WHERE node_uuid=%s"""

            uvalues = (
                       self.node_name, 
                       self.node_model, 
                       self.node_serial_number, 
                       self.node_system_id, 
                       self.node_storage_configuration,
                       self.node_location, 
                       self.node_version, 
                       self.stg_uuid, 
                       self.customer_id, 
                       self.datacenter_id, 
                       self.node_mgmt_lif,
                       self.node_service_processor,
                       self.node_uuid
                      )

            cursor.execute(uquery, uvalues) 
            conn.commit()
            print("Node Name: ", self.node_name)
            print("Node UUID: ", self.node_uuid)
            print("ONTAP node info updated successfully.")
            return 0
        #except mysql.connector.Error as err:
        except:
            #print(f"Error updating ONTAP node info: {err}")
            return 1
    
    def insert_stg_node_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            iquery = """INSERT INTO t_stg_node_info 
                        (
                         node_name, 
                         node_uuid, 
                         node_model, 
                         node_serial_number,
                         node_system_id, 
                         node_storage_configuration, 
                         node_location, 
                         node_version, 
                         stg_uuid,
                         customer_id, 
                         datacenter_id,
                         node_mgmt_lif,
                         node_service_processor
                         ) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            ivalues = (
                       self.node_name, 
                       self.node_uuid, 
                       self.node_model, 
                       self.node_serial_number, 
                       self.node_system_id,
                       self.node_storage_configuration, 
                       self.node_location, 
                       self.node_version, 
                       self.stg_uuid, 
                       self.customer_id, 
                       self.datacenter_id,
                       self.node_mgmt_lif,
                       self.node_service_processor
            )
            cursor.execute(iquery, ivalues) 
            conn.commit()
            print("Node Name: ", self.node_name)
            print("Node UUID: ", self.node_uuid)
            print("ONTAP node info inserted successfully.")
            return 0
        except mysql.connector.Error as err:
            print(f"Error inserting ONTAP node info: {err}")
            return 1
    
    def insert_or_update_ontap_node_info(self, conn, json_node_info, json1_info, json2_info, stg_uuid, customer_id, datacenter_id):
        try:
            node_info = json_node_info.get('ontap_info', {}).get('cluster/nodes', {}).get('records', [])
    
            # Debugging JSON content
            print("json_node_info content:", json_node_info)
            print("json1_info content:", json1_info)
            print("json2_info content:", json2_info)
    
            sp_ip_map = {rec['node']: rec.get('ip_address', 'Unknown') for rec in json1_info.get('msg', {}).get('records', [])}
            mgmt_ip_map = {rec['curr_node']: rec.get('address', 'Unknown') for rec in json2_info.get('msg', {}).get('records', [])}
    
            print("Management IP Map:", mgmt_ip_map)
            print("Service Processor IP Map:", sp_ip_map)
    
            for node in node_info:
                node_name = node.get('name')
                mgmt_ip = mgmt_ip_map.get(node_name, 'Unknown')
                sp_ip = sp_ip_map.get(node_name, 'Unknown')
    
                print(f"Processing node {node_name} with mgmt IP {mgmt_ip} and SP IP {sp_ip}")
    
                self.extract_info(node, mgmt_ip, sp_ip, stg_uuid, customer_id, datacenter_id)
                node_uuid = node.get('uuid')
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM t_stg_node_info WHERE node_uuid = %s", (node_uuid,))
                existing_record = cursor.fetchone()
                if existing_record:
                    update_result = self.update_ontap_node_info(conn)
                    if update_result != 0:
                        return update_result
                else:
                    insert_result = self.insert_stg_node_info(conn)
                    if insert_result != 0:
                        return insert_result
            return 0
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return 1
 
def main():
    try:
        # Connect to the database
        sys_db_run = c_SystemDBrunFunctions()
        # Connect to the MariaDB database
        conn = sys_db_run.connect_to_database()
        if not conn:
            return 1 # Return error code 1 if connection fails

        sys_db_run.delete_json_file(json_display_ontap_node_info_rest)
        sys_db_run.delete_json_file(json_display_ontap_node_info_rest1)
        sys_db_run.delete_json_file(json_display_ontap_node_info_rest2)

        # Create an instance of c_ONTAPInfo_node
        ontap_node_info_handler = c_ONTAPInfo_node()
        
        # Print each field from the query
        sql = "SELECT t_stg_info.stg_name,t_stg_info.stg_uuid,t_stg_info.stg_mgmt_ip,t_stg_info.customer_id,t_stg_info.datacenter_id FROM t_stg_info JOIN t_stg_access_data ON t_stg_info.stg_mgmt_ip = t_stg_access_data.storageip WHERE t_stg_access_data.enabled = 1"
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
            print(f"Storage Name: {result['stg_name']}, UUID: {result['stg_uuid']}, Management IP: {result['stg_mgmt_ip']}, Customer ID: {result['customer_id']}, Datacenter ID: {result['datacenter_id']}")
            
            if sys_db_run.check_ip_accessibility(result['stg_mgmt_ip']):
                # Fetch node information from the JSON file
                    
                status1 = sys_db_run.run_ansible_playbook2(p_book_ontap_node_info,result['stg_mgmt_ip'],json_display_ontap_node_info_rest,conn)
                status2 = sys_db_run.run_ansible_playbook2(p_book_ontap_node_info,result['stg_mgmt_ip'],json_display_ontap_node_info_rest1,conn)
                status3 = sys_db_run.run_ansible_playbook2(p_book_ontap_node_info,result['stg_mgmt_ip'],json_display_ontap_node_info_rest2,conn)

                if status1 and status2 and status3:
                    json_node_info = sys_db_run.load_json(json_display_ontap_node_info_rest)
                    json1_info = sys_db_run.load_json(json_display_ontap_node_info_rest1)
                    json2_info = sys_db_run.load_json(json_display_ontap_node_info_rest2)

                    # Insert or update node information into t_stg_node_info table
                    result_write = ontap_node_info_handler.insert_or_update_ontap_node_info(conn, json_node_info,json1_info, json2_info, result['stg_uuid'], result['customer_id'], result['datacenter_id'])
                    if result_write != 0:
                        return result_write

        # Close database connection
        conn.close()
        return 0
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
