import os
import sys
import json
import mysql.connector
import shutil

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
json_display_ontap_svm_peer_info_rest = os.path.abspath("ymls/json/Display_ontap_svm_peer_info_rest.json")
p_book_ontap_svm_peer_info_rest = os.path.abspath("ymls/11_Display_ontap_svm_peer_info_rest.yml")

class c_ONTAPInfo_peer:
    def __init__(self):
        self.ontap_svm_info_peer = None
        self.stg_name = None
        self.stg_uuid = None
        self.peer_uuid = None
        self.peer_name = None
        self.svm_name = None
        self.svm_uuid = None
        self.peer_state = None
        self.peer_svm_name = None
        self.peer_svm_uuid = None
        self.peer_cluster_name = None
        self.peer_cluster_uuid = None 
        self.applications = None
        self.stg_uuid_peer_uuid = None

    def extract_info(self, stg_name, stg_uuid, record):
        # Load ONTAP info from JSON file
        if not record:
            print("No JSON data loaded.")
            return 1
        self.stg_name = stg_name
        self.stg_uuid = stg_uuid
        self.peer_uuid = record.get("uuid")
        self.peer_name = record.get("name")
        self.svm_name = record.get('svm', {}).get('name')
        self.svm_uuid = record.get('svm', {}).get('uuid')
        self.peer_state = record.get('state')
        self.peer_svm_name = record.get('peer', {}).get('svm', {}).get('name')
        self.peer_svm_uuid = record.get('peer', {}).get('svm', {}).get('uuid')
        self.peer_cluster_name = record.get('peer', {}).get('cluster', {}).get('name')
        self.peer_cluster_uuid = record.get('peer', {}).get('cluster', {}).get('uuid')
        self.applications = json.dumps(record.get('applications', []))
        self.stg_uuid_peer_uuid = self.stg_uuid + self.peer_uuid
        #self.peer_applications = ",".join(record.get("peer_applications", ["None"]))

    def ontap_peer_info_insert_record(self, conn):
        try:
            cursor = conn.cursor()

            iquery = """INSERT INTO t_svm_peer_info
                     (
                      stg_name,
                      stg_uuid,
                      peer_uuid,
                      peer_name,
                      svm_name,
                      svm_uuid,
                      peer_state,
                      peer_svm_name,
                      peer_svm_uuid,
                      peer_cluster_name,
                      peer_cluster_uuid,
                      applications,
                      stg_uuid_peer_uuid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            ivalues = (
                       self.stg_name,
                       self.stg_uuid,
                       self.peer_uuid,
                       self.peer_name,
                       self.svm_name,
                       self.svm_uuid,
                       self.peer_state,
                       self.peer_svm_name,
                       self.peer_svm_uuid,
                       self.peer_cluster_name,
                       self.peer_cluster_uuid ,
                       self.applications,
                       self.stg_uuid_peer_uuid
            )
            cursor.execute(iquery, ivalues)
            conn.commit()
            print(f"Record: {self.stg_uuid_peer_uuid} inserted successfully.")
        except mysql.connector.Error as error:
            print(f"Error inserting record: {error}")

    def ontap_peer_info_update_record(self, conn):
        try:
            cursor = conn.cursor()
            uquery = """UPDATE t_svm_peer_info 
                    SET  stg_name = %s,
                         stg_uuid = %s,
                         peer_uuid = %s,
                         peer_name = %s,
                         svm_name = %s,
                         svm_uuid = %s,
                         peer_state = %s,
                         peer_svm_name = %s,
                         peer_svm_uuid = %s,
                         peer_cluster_name = %s,
                         peer_cluster_uuid = %s,
                         applications = %s
                    WHERE stg_uuid_peer_uuid = %s"""
            uvalues = (
                       self.stg_name,
                       self.stg_uuid,
                       self.peer_uuid,
                       self.peer_name,
                       self.svm_name,
                       self.svm_uuid,
                       self.peer_state,
                       self.peer_svm_name,
                       self.peer_svm_uuid,
                       self.peer_cluster_name,
                       self.peer_cluster_uuid ,
                       self.applications,
                       self.stg_uuid_peer_uuid
            )
            cursor.execute(uquery, uvalues)
            conn.commit()
            print(f"Record: {self.stg_uuid_peer_uuid} updated successfully.")
        except mysql.connector.Error as error:
            print(f"Error updating record: {error}")

    def ontap_peer_info_insert_update_record(self, conn, stg_uuid, record):
        cursor = conn.cursor()
        stg_peer_uuid = record.get("uuid")
        stg_uuid_peer_uuid = str(stg_uuid) + str(stg_peer_uuid)
        if stg_uuid_peer_uuid is None:
            stg_uuid_peer_uuid = "NULL"  # Set to NULL if UUID is None
        # Check if the record already exists in the database based on stg_uuid
        query = "SELECT COUNT(*) FROM t_svm_peer_info WHERE stg_uuid_peer_uuid = %s"
        cursor.execute(query, (stg_uuid_peer_uuid,))
        result = cursor.fetchone()

        if result[0] > 0:
            # Record with same stg_uuid and stg_peer_uuid exists, update it
            self.ontap_peer_info_update_record(conn)
        else:
            # Record does not exist, insert it
            self.ontap_peer_info_insert_record(conn)

    def ontap_svm_peer_info_process_records(self, conn, stg_name, stg_uuid, json_ontap_svm_peer_info):

        records = json_ontap_svm_peer_info["ontap_info"]["svm/peers"]["records"]
        if records:
          #print(records)
            for record in records:
                self.extract_info(stg_name, stg_uuid, record)
                self.ontap_peer_info_insert_update_record(conn, stg_uuid, record)
            print("Records inserted or updated successfully.")
        else:
            print("No records found in JSON.")


# Main function
def main():

    # Connect to the database
    sys_db_run = c_SystemDBrunFunctions()
    # Connect to the MariaDB database
    conn = sys_db_run.connect_to_database()
    if not conn:
        return 1  # Return error code 1 if connection fails

    sys_db_run.delete_json_file(json_display_ontap_svm_peer_info_rest)

    ontap_svm_info_peer = c_ONTAPInfo_peer()
    # Print each field from the query
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

    results_list = sys_db_run.run_sql_query(conn,sql)
    for result in results_list:
        print(f"Storage Name: {result['stg_name']}, UUID: {result['stg_uuid']}, Management IP: {result['stg_mgmt_ip']}, customer_id: {result['customer_id']}")
        if sys_db_run.check_ip_accessibility(result['stg_mgmt_ip']):

            status = sys_db_run.run_ansible_playbook2(p_book_ontap_svm_peer_info_rest,result['stg_mgmt_ip'],json_display_ontap_svm_peer_info_rest,conn )
            if status:
                json_ontap_svm_peer_info = sys_db_run.load_json(json_display_ontap_svm_peer_info_rest)
                ontap_svm_info_peer.ontap_svm_peer_info_process_records(conn, result['stg_name'],result['stg_uuid'],json_ontap_svm_peer_info)

    # Close database connection
    conn.close()
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)

