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
json_display_svm_info_rest = os.path.abspath("ymls/json/Display_svm_info_rest.json")
p_book_svm_info = os.path.abspath("ymls/06_Display_svm_info_rest.yml")

class c_ONTAPInfo_svm:
    def __init__(self):
        self.stg_name = None 
        self.stg_uuid = None 
        self.stg_uuid_svm_uuid = None 
        self.svm_name = None 
        self.svm_uuid = None 
        self.svm_language = None 
        self.svm_state = None 
        self.svm_subtype = None 
        self.svm_comment = None 
        self.svm_aggregates_name = None 
        self.svm_aggregates_uuid = None 
        self.svm_ip_address = None 
        self.svm_ip_name = None 
        self.svm_cifs_allowed = None 
        self.svm_cifs_enabled = None 
        self.svm_fcp_allowed = None 
        self.svm_fcp_enabled = None 
        self.svm_iscsi_allowed = None 
        self.svm_iscsi_enabled = None 
        self.svm_nfs_allowed = None 
        self.svm_nfs_enabled = None 
        self.svm_s3_allowed = None 
        self.svm_s3_enabled = None 
        self.svm_nvme_allowed = None 
        self.svm_nvme_enabled = None 
        self.svm_snapshot_policy = None 
        self.svm_ipspace_name = None 

    def extract_info(self, stg_name, stg_uuid ,record):
        # Load ONTAP info from JSON file
        if not record:
            print("No JSON data loaded.")
            return 1
        #print("Record:", record)  # Debug statement
        self.stg_name = stg_name
        self.stg_uuid = stg_uuid 
        self.svm_name = record['name']
        self.svm_uuid = record['uuid']
        self.stg_uuid_svm_uuid = ''.join([self.svm_uuid, self.stg_uuid]) 
        self.svm_language = record['language']
        self.svm_state = record['state']
        self.svm_subtype = record['subtype']
        self.svm_comment = record['comment']

        if 'aggregates' in record and record['aggregates'] is not None:
            self.svm_aggregates_name = record['aggregates'][0]['name']
            self.svm_aggregates_uuid = record['aggregates'][0]['uuid']
        else:
            self.svm_aggregates_name = None
            self.svm_aggregates_uuid = None

        #self.svm_aggregates_name = record['aggregates'][0]['name']
        #self.svm_aggregates_uuid = record['aggregates'][0]['uuid']

        # Check if 'ip_interfaces' exists in the record
        if 'ip_interfaces' in record:
            self.svm_ip_address = record['ip_interfaces'][0]['ip']['address']
            self.svm_ip_name = record['ip_interfaces'][0]['name']
        else:
            self.svm_ip_address = None
            self.svm_ip_name = None

        # Check if other fields exist in the record and handle them similarly
        self.svm_cifs_allowed = record['cifs'].get('allowed') if 'cifs' in record else None
        self.svm_cifs_enabled = record['cifs'].get('enabled') if 'cifs' in record else None
        self.svm_fcp_allowed = record['fcp'].get('allowed') if 'fcp' in record else None
        self.svm_fcp_enabled = record['fcp'].get('enabled') if 'fcp' in record else None
        self.svm_iscsi_allowed = record['iscsi'].get('allowed') if 'iscsi' in record else None
        self.svm_iscsi_enabled = record['iscsi'].get('enabled') if 'iscsi' in record else None
        self.svm_nfs_allowed = record['nfs'].get('allowed') if 'nfs' in record else None
        self.svm_nfs_enabled = record['nfs'].get('enabled') if 'nfs' in record else None
        self.svm_s3_allowed = record['s3'].get('allowed') if 's3' in record else None
        self.svm_s3_enabled = record['s3'].get('enabled') if 's3' in record else None
        self.svm_nvme_allowed = record['nvme'].get('allowed') if 'nvme' in record else None
        self.svm_nvme_enabled = record['nvme'].get('enabled') if 'nvme' in record else None
        self.svm_snapshot_policy = record['snapshot_policy'].get('name') if 'snapshot_policy' in record else None
        self.svm_ipspace_name = record['ipspace'].get('name') if 'ipspace' in record else None


    def print_vars(self):
        print(f"self.stg_name: {self.stg_name}") 
        print(f"self.stg_uuid: {self.stg_uuid}") 
        print(f"self.stg_uuid_svm_uuid: {self.stg_uuid_svm_uuid}") 
        print(f"self.svm_name: {self.svm_name}")
        print(f"self.svm_uuid: {self.svm_uuid}") 
        print(f"self.svm_language: {self.svm_language}") 
        print(f"self.svm_state: {self.svm_state}") 
        print(f"self.svm_subtype: {self.svm_subtype}") 
        print(f"self.svm_comment: {self.svm_comment}") 
        print(f"self.svm_aggregates_name: {self.svm_aggregates_name}") 
        print(f"self.svm_aggregates_uuid: {self.svm_aggregates_uuid}") 
        print(f"self.svm_ip_address: {self.svm_ip_address}") 
        print(f"self.svm_ip_name: {self.svm_ip_name}") 
        print(f"self.svm_cifs_allowed: {self.svm_cifs_allowed}") 
        print(f"self.svm_cifs_enabled: {self.svm_cifs_enabled}") 
        print(f"self.svm_fcp_allowed: {self.svm_fcp_allowed}") 
        print(f"self.svm_fcp_enabled: {self.svm_fcp_enabled}") 
        print(f"self.svm_iscsi_allowed: {self.svm_iscsi_allowed}") 
        print(f"self.svm_iscsi_enabled: {self.svm_iscsi_enabled}") 
        print(f"self.svm_nfs_allowed: {self.svm_nfs_allowed}") 
        print(f"self.svm_nfs_enabled: {self.svm_nfs_enabled}") 
        print(f"self.svm_s3_allowed: {self.svm_s3_allowed}") 
        print(f"self.svm_s3_enabled: {self.svm_s3_enabled}") 
        print(f"self.svm_nvme_allowed: {self.svm_nvme_allowed}") 
        print(f"self.svm_nvme_enabled: {self.svm_nvme_enabled}") 
        print(f"self.svm_snapshot_policy: {self.svm_snapshot_policy}") 
        print(f"self.svm_ipspace_name: {self.svm_ipspace_name}") 

    def insert_svm_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            iquery = """INSERT INTO t_svms 
                                    (
                                     stg_name,
                                     stg_uuid,
                                     stg_uuid_svm_uuid,
                                     svm_name, 
                                     svm_uuid, 
                                     svm_language, 
                                     svm_state, 
                                     svm_subtype, 
                                     svm_comment, 
                                     svm_aggregates_name, 
                                     svm_aggregates_uuid, 
                                     svm_ip_address, 
                                     svm_ip_name, 
                                     svm_cifs_allowed, 
                                     svm_cifs_enabled, 
                                     svm_fcp_allowed, 
                                     svm_fcp_enabled, 
                                     svm_iscsi_allowed, 
                                     svm_iscsi_enabled, 
                                     svm_nfs_allowed, 
                                     svm_nfs_enabled, 
                                     svm_s3_allowed, 
                                     svm_s3_enabled, 
                                     svm_nvme_allowed, 
                                     svm_nvme_enabled, 
                                     svm_snapshot_policy, 
                                     svm_ipspace_name) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s)"""
            ivalues = (
                       self.stg_name,
                       self.stg_uuid,
                       self.stg_uuid_svm_uuid,
                       self.svm_name, 
                       self.svm_uuid, 
                       self.svm_language, 
                       self.svm_state, 
                       self.svm_subtype, 
                       self.svm_comment, 
                       self.svm_aggregates_name, 
                       self.svm_aggregates_uuid, 
                       self.svm_ip_address, 
                       self.svm_ip_name, 
                       self.svm_cifs_allowed, 
                       self.svm_cifs_enabled, 
                       self.svm_fcp_allowed, 
                       self.svm_fcp_enabled, 
                       self.svm_iscsi_allowed, 
                       self.svm_iscsi_enabled, 
                       self.svm_nfs_allowed, 
                       self.svm_nfs_enabled, 
                       self.svm_s3_allowed, 
                       self.svm_s3_enabled, 
                       self.svm_nvme_allowed, 
                       self.svm_nvme_enabled, 
                       self.svm_snapshot_policy, 
                       self.svm_ipspace_name
                     )
            cursor.execute(iquery, ivalues)
            conn.commit()
            print("SVM: ", self.svm_name," information inserted successfully!")
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
    
    
    def update_svm_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            uquery = """UPDATE t_svms 
                      SET 
                         stg_name = %s,
                         stg_uuid = %s,
                         svm_name = %s, 
                         svm_uuid = %s, 
                         svm_language = %s, 
                         svm_state = %s, 
                         svm_subtype = %s, 
                         svm_comment = %s, 
                         svm_aggregates_name = %s, 
                         svm_aggregates_uuid = %s, 
                         svm_ip_address = %s, 
                         svm_ip_name = %s, 
                         svm_cifs_allowed = %s, 
                         svm_cifs_enabled = %s, 
                         svm_fcp_allowed = %s, 
                         svm_fcp_enabled = %s, 
                         svm_iscsi_allowed = %s, 
                         svm_iscsi_enabled = %s, 
                         svm_nfs_allowed = %s, 
                         svm_nfs_enabled = %s, 
                         svm_s3_allowed = %s, 
                         svm_s3_enabled = %s, 
                         svm_nvme_allowed = %s, 
                         svm_nvme_enabled = %s, 
                         svm_snapshot_policy = %s, 
                         svm_ipspace_name = %s 
                      WHERE stg_uuid_svm_uuid = %s"""
            
            uvalues = (
                       self.stg_name,
                       self.stg_uuid,
                       self.svm_name, 
                       self.svm_uuid, 
                       self.svm_language, 
                       self.svm_state, 
                       self.svm_subtype, 
                       self.svm_comment, 
                       self.svm_aggregates_name, 
                       self.svm_aggregates_uuid, 
                       self.svm_ip_address, 
                       self.svm_ip_name, 
                       self.svm_cifs_allowed, 
                       self.svm_cifs_enabled, 
                       self.svm_fcp_allowed, 
                       self.svm_fcp_enabled, 
                       self.svm_iscsi_allowed, 
                       self.svm_iscsi_enabled, 
                       self.svm_nfs_allowed, 
                       self.svm_nfs_enabled, 
                       self.svm_s3_allowed, 
                       self.svm_s3_enabled, 
                       self.svm_nvme_allowed, 
                       self.svm_nvme_enabled, 
                       self.svm_snapshot_policy, 
                       self.svm_ipspace_name,
                       self.stg_uuid_svm_uuid
                      )
            cursor.execute(uquery, uvalues)
            conn.commit()
            print("SVM: ", self.svm_name," information updated successfully!")
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
    
    def insert_or_update_svm_info(self, conn, stg_name, stg_uuid, svm_info):
        try:
            cursor = conn.cursor(dictionary=True)
            stg_svm_info = svm_info['ontap_info']['svm/svms']['records'] 
            for record in stg_svm_info:
                svm_uuid = record['uuid']
                stg_uuid_svm_uuid = ''.join([svm_uuid, stg_uuid])
                self.extract_info(stg_name, stg_uuid ,record)
                print(f"stg_uuid_svm_uuid: {stg_uuid_svm_uuid}")
                #self.print_vars()
                # Check if the svm_uuid already exists in the database
                cursor.execute("SELECT * FROM t_svms WHERE stg_uuid_svm_uuid = %s", (stg_uuid_svm_uuid,))
                existing_record = cursor.fetchone()
                if existing_record:
                    # If the record exists, update it
                    print("Record exists, updating...")
                    self.update_svm_info(conn)
                else:
                    # If the record doesn't exist, insert it
                    print("Record does not exist, inserting...")
                    self.insert_svm_info(conn)

            print("SVM information added or updated successfully!")
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

        sys_db_run.delete_json_file(json_display_svm_info_rest)
       
        # Create an instance of c_ONTAPInfo_svm
        ontap_svm_info_handler = c_ONTAPInfo_svm()

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
            stg_name = result['stg_name']
            stg_uuid = result['stg_uuid']
            stg_ip = result['stg_mgmt_ip']
            print(f"Storage Name: {stg_name}, UUID: {stg_uuid}, Management IP: {stg_ip}")
            
            if sys_db_run.check_ip_accessibility(stg_ip):
                # Fetch node information from the JSON file
                status = sys_db_run.run_ansible_playbook2(p_book_svm_info, result['stg_mgmt_ip'],json_display_svm_info_rest,conn)
                if status:
                    json_svm_info = sys_db_run.load_json(json_display_svm_info_rest)
    
                    if json_svm_info is None:
                        return 6  # Return error code 6 if JSON loading fails
                    # Insert or update SVM information into t_svms table
                    result = ontap_svm_info_handler.insert_or_update_svm_info(conn, stg_name, stg_uuid, json_svm_info)
                    if result != 0:
                        return result  # Return the error code from insert_or_update_aggregate_info

        # Close database connection
        conn.close()
    except mysql.connector.Error as err:
        print("MySQL Error:", err)

if __name__ == "__main__":
    main()

