import os
import sys
import json
import mysql.connector
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

# Define the files path
json_display_vol_info_rest = os.path.abspath('ymls/json/Display_volume_information_rest.json')
json_display_vol_info_rest2 = os.path.abspath('ymls/json/Display_volume_information_rest.json2')
json_display_vol_info_rest3 = os.path.abspath('ymls/json/Display_volume_information_rest.json3')
p_book_vol_info = os.path.abspath("ymls/08_Display_volume_information_rest.yml")

def format_elapsed_time(elapsed_time):
    if elapsed_time < 60:
        return f"{elapsed_time:.2f} seconds"
    else:
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        return f"{minutes} minutes and {seconds:.2f} seconds"

class c_ONTAPInfo_vol:
    def __init__(self):

        self.vol_name = None 
        self.vol_uuid = None 
        self.stg_uuid_vol_uuid = None
        self.stg_name = None
        self.vol_state = None 
        self.vol_type = None 
        self.vol_style = None 
        self.vol_size = None 
        self.vol_comment = None 
        self.vol_creation_time = None 
        self.vol_language = None 
        self.vol_snapshot_policy = None 
        self.vol_nas_export_policy = None 
        self.vol_svm_name = None 
        self.vol_svm_uuid = None 
        self.vol_is_flexclone = None 
        self.vol_snapmirror_protected = None 
        self.vol_aggregate_name = None 
        self.vol_aggregate_uuid = None 
        self.snapshot_count = None
        self.access_protocols = None
        self.junction_path = None
        self.activity_tracking_unsupported_reason = None 

    def extract_info(self, stg_name, stg_uuid ,volume):
        # Load ONTAP info from JSON file
        if not volume:
            print("No JSON data loaded.")
            return 1
        # Extracting fields as variables
        self.vol_name = volume['name']
        self.vol_uuid = volume['uuid']
        self.stg_uuid_vol_uuid = ''.join([stg_uuid, self.vol_uuid]) 
        self.stg_name = stg_name
        self.vol_state = volume.get('state', 'Unknown')  # Set default value if 'state' key is missing
        self.vol_type = volume['type']
        self.vol_style = volume['style']
        self.vol_size = str( int(volume.get('size', 0)) / 1024 / 1024 / 1024)  # Set default value if 'size' key is missing
        self.vol_comment = volume['comment']
        self.vol_creation_time = volume['create_time']
        self.vol_language = volume.get('language', 'Unknown')  # Set default value if 'language' key is missing
        self.vol_snapshot_policy = volume['snapshot_policy']['name']
        self.vol_nas_export_policy = volume['nas']['export_policy']['name']
        self.vol_svm_name = volume['svm']['name']
        self.vol_svm_uuid = volume['svm']['uuid']
        self.vol_is_flexclone = volume['clone']['is_flexclone']
        self.vol_snapmirror_protected = volume['snapmirror']['is_protected']
        self.vol_aggregate_name = volume['aggregates'][0]['name']
        self.vol_aggregate_uuid = volume['aggregates'][0]['uuid']
        self.snapshot_count = volume.get('snapshot_count', 0)

    def extract_info2(self, json_data2):
        for record in json_data2['msg']['records']:
            if record['volume'] == self.vol_name:
                self.activity_tracking_unsupported_reason = str(record.get('activity_tracking_unsupported_reason', None))
                self.junction_path = record.get('junction_path', None)
    
                # Simplifying protocol checks by defining flags
                #has_luns = ('LUNs' in self.activity_tracking_unsupported_reason and self.vol_type == "rw")
                is_nfs = (('nfs' in self.vol_svm_name or 'nfs' in self.vol_name) and self.vol_type == "rw")
                is_cifs = (('cifs' in self.vol_svm_name or 'cifs' in self.vol_name) and self.vol_type == "rw")
           
                # Determine access protocols
                if (self.junction_path and is_nfs):
                    self.access_protocols = 'NFS'
                elif (self.junction_path and is_cifs):
                    self.access_protocols = 'CIFS'
                else:
                    self.access_protocols = None

    def extract_info3(self, json_data3):
        for record in json_data3.get('msg', {}).get('records', []):
            if 'volume' in record and record['volume'] == self.vol_name:
                    self.access_protocols = 'CIFS'
            
                    

    def insert_volume_info(self, conn):
        try:
            cursor = conn.cursor(dictionary=True)
            iquery = """INSERT INTO t_volumes 
                                            (
                                             vol_name, 
                                             vol_uuid, 
                                             stg_uuid_vol_uuid, 
                                             stg_name,
                                             vol_state, 
                                             vol_type, 
                                             vol_style, 
                                             vol_size, 
                                             vol_comment, 
                                             vol_creation_time,
                                             vol_language, 
                                             vol_snapshot_policy, 
                                             vol_nas_export_policy, 
                                             vol_svm_name, 
                                             vol_svm_uuid,
                                             vol_is_flexclone, 
                                             vol_snapmirror_protected, 
                                             vol_aggregates_name, 
                                             vol_aggregates_uuid,
                                             snapshot_count,
                                             activity_tracking_unsupported_reason,
                                             junction_path,
                                             access_protocols
                                            )
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            ivalues = ( 
                       self.vol_name, 
                       self.vol_uuid, 
                       self.stg_uuid_vol_uuid,
                       self.stg_name, 
                       self.vol_state, 
                       self.vol_type, 
                       self.vol_style, 
                       self.vol_size,
                       self.vol_comment, 
                       self.vol_creation_time, 
                       self.vol_language, 
                       self.vol_snapshot_policy,
                       self.vol_nas_export_policy, 
                       self.vol_svm_name, 
                       self.vol_svm_uuid, 
                       self.vol_is_flexclone,
                       self.vol_snapmirror_protected, 
                       self.vol_aggregate_name, 
                       self.vol_aggregate_uuid,
                       self.snapshot_count,
                       self.activity_tracking_unsupported_reason,
                       self.junction_path,
                       self.access_protocols
                      )
            
            cursor.execute(iquery, ivalues)
            conn.commit()
            print("Volume: ", self.vol_name, " inserted successfully!")
            return True
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return False

    def update_volumes_access_protocols(self, conn):
        try:
    
            cursor = conn.cursor(dictionary=True)

            #-- Set access_protocols to 'dp_vol' where vol_type is 'dp'
            update_dp_query = """UPDATE t_volumes 
                                 SET 
                                     access_protocols = 'dp_vol'                        
                                 WHERE  vol_type = 'dp';
                              """
    
            cursor.execute(update_dp_query)

            #-- Set access_protocols to 'dp_vol' where vol_type is 'dp'
            update_root_query = """UPDATE t_volumes 
                                   SET 
                                      access_protocols = 'root_vol'                        
                                   WHERE  vol_name LIKE '%root%';
                                """
    
            cursor.execute(update_root_query)

            #-- Set access_protocols to 'iSCSI or FC LUN' where activity_tracking_unsupported_reason contains 'LUNs'
            update_lun_query = """UPDATE t_volumes 
                                   SET 
                                      access_protocols = 'iSCSI or FC LUN'                        
                                   WHERE  activity_tracking_unsupported_reason LIKE '%LUNs%';
                                """
    
            cursor.execute(update_lun_query)

            #-- Set access_protocols to 'mc_vol' where junction_path like "%/(%"
            update_mc_query = """UPDATE t_volumes 
                                   SET 
                                      access_protocols = 'mc_vol'                        
                                   WHERE  junction_path  like "%/(%";
                                """
    
            cursor.execute(update_mc_query)

            #-- Set access_protocols to 'mc_vol' where junction_path  
            update_mc_query2 = """UPDATE t_volumes tv
                                 JOIN t_svms ts ON tv.vol_svm_name = ts.svm_name
                                 SET tv.access_protocols = 'mc_vol'
                                 WHERE tv.access_protocols IS NULL
                                 AND ts.svm_state = 'stopped'
                                 AND ts.svm_subtype = 'sync_destination';
                                """
    
            cursor.execute(update_mc_query2)

            #-- Set access_protocols to 'mc_vol' where junction_path like "%/(%"
            update_nfs_none_query = """ UPDATE t_volumes
                                  SET access_protocols = CASE
                                      WHEN vol_nas_export_policy != 'default' AND junction_path IS NOT NULL THEN 'NFS'
                                      WHEN vol_nas_export_policy = 'default' AND junction_path IS NULL THEN 'None'
                                      WHEN vol_nas_export_policy = 'default' AND junction_path IS NOT NULL THEN 'None'
                                      WHEN vol_nas_export_policy != 'default' AND junction_path IS NULL THEN 'None'
                                      ELSE access_protocols
                                  END
                                  WHERE access_protocols IS NULL;
                              """
    
            cursor.execute(update_nfs_none_query)

            conn.commit()
            print("Updated access_protocols for dp, root, and mc volumes.")
        except mysql.connector.Error as err:
            print("MySQL Error:", err)

    def update_volume_info(self, conn):
        try:
    
            cursor = conn.cursor(dictionary=True)
            uquery = """UPDATE t_volumes 
                        SET 
                         vol_name = %s, 
                         vol_uuid = %s, 
                         stg_name  = %s,
                         vol_state = %s,
                         vol_type = %s, 
                         vol_style = %s,
                         vol_size = %s, 
                         vol_comment = %s, 
                         vol_creation_time = %s, 
                         vol_language = %s,
                         vol_snapshot_policy = %s, 
                         vol_nas_export_policy = %s, 
                         vol_svm_name = %s,
                         vol_svm_uuid = %s, 
                         vol_is_flexclone = %s, 
                         vol_snapmirror_protected = %s,
                         vol_aggregates_name = %s, 
                         vol_aggregates_uuid = %s,
                         snapshot_count = %s,
                         activity_tracking_unsupported_reason = %s,
                         junction_path = %s,
                         access_protocols = %s
                        WHERE stg_uuid_vol_uuid = %s"""
    
            uvalues = ( 
                       self.vol_name, 
                       self.vol_uuid,
                       self.stg_name,
                       self.vol_state, 
                       self.vol_type, 
                       self.vol_style, 
                       self.vol_size, 
                       self.vol_comment, 
                       self.vol_creation_time,
                       self.vol_language, 
                       self.vol_snapshot_policy, 
                       self.vol_nas_export_policy, 
                       self.vol_svm_name,
                       self.vol_svm_uuid, 
                       self.vol_is_flexclone, 
                       self.vol_snapmirror_protected, 
                       self.vol_aggregate_name,
                       self.vol_aggregate_uuid, 
                       self.snapshot_count,
                       self.activity_tracking_unsupported_reason,
                       self.junction_path,
                       self.access_protocols,
                       self.stg_uuid_vol_uuid
                      )
    
            cursor.execute(uquery, uvalues)
            conn.commit()
            print("Volume: ", self.vol_name, " updated successfully!")
            return True
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return False
    
    

    def insert_or_update_vol_info(self, conn, stg_name, stg_uuid, json_vol_info, json_vol_info2,json_vol_info3):
        try:
            cursor = conn.cursor(dictionary=True)
            volumes = json_vol_info['ontap_info']['storage/volumes']['records']
            for record in volumes:
                vol_uuid = record['uuid']
                stg_uuid_vol_uuid = ''.join([stg_uuid, vol_uuid])
                self.extract_info(stg_name, stg_uuid ,record)
                self.extract_info2(json_vol_info2)
                self.extract_info3(json_vol_info3)
                print(f"stg_uuid_vol_uuid: {stg_uuid_vol_uuid}")

                cursor.execute("SELECT * FROM t_volumes WHERE stg_uuid_vol_uuid = %s", (stg_uuid_vol_uuid,))
                existing_record = cursor.fetchone()
                if existing_record:
                    # If the record exists, update it
                    print("Record exists, updating...")
                    update_result = self.update_volume_info(conn)
                    if not update_result:
                        return False
                    #else:
                        #print("Volume:", self.vol_name,"Access protocol:", self.access_protocols, "information updated successfully!")
                else:
                    # If the record doesn't exist, insert it
                    print("Record does not exist, inserting...")
                    insert_result = self.insert_volume_info(conn)
                    if not insert_result:
                        return False
                    #else:
                        #print("Volume:", self.vol_name,"Access protocol:", self.access_protocols, "information  add successfully!")
            #print("Volume:", self.vol_name,"Access protocol:", self.access_protocols, "information added or updated successfully!")
            return 0  # Success
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return 3  # Return error code 3 for MySQL errors
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return 4  # Return error code 4 for other exceptions

    def remove_volumes_not_in_json(self, conn, stg_uuid, json_vol_info):
        try:
            cursor = conn.cursor(dictionary=True)
            # Get the current volumes from the JSON file
            json_volumes = {record['uuid'] for record in json_vol_info['ontap_info']['storage/volumes']['records']}
            #delete  from t_volumes; # Delete All Records of t_volumes
            # Fetch existing volumes from the database
            cursor.execute("SELECT vol_uuid FROM t_volumes WHERE stg_uuid_vol_uuid LIKE %s", (f"{stg_uuid}%",))
            db_volumes = {record['vol_uuid'] for record in cursor.fetchall()}

            # Identify volumes in the database but not in the JSON file
            volumes_to_remove = db_volumes - json_volumes

            # Remove volumes not in the JSON file
            if volumes_to_remove:
                for vol_uuid in volumes_to_remove:
                    cursor.execute("DELETE FROM t_volumes WHERE vol_uuid = %s AND stg_uuid_vol_uuid LIKE %s", (vol_uuid, f"{stg_uuid}%"))
                conn.commit()
                print(f"Removed volumes not in JSON: {volumes_to_remove}")
            else:
                print("No volumes to remove.")

            return 0  # Success
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return 3  # Return error code 3 for MySQL errors
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return 4  # Return error code 4 for other exceptions


def main():

    try:
        start_time = time.time()  # Record the start time
        # Connect to the MariaDB database
        sys_db_run = c_SystemDBrunFunctions()
        conn = sys_db_run.connect_to_database()
        if not conn:
            return 5  # Return error code 5 if connection fails

        sys_db_run.delete_json_file(json_display_vol_info_rest)
        sys_db_run.delete_json_file(json_display_vol_info_rest2)
        sys_db_run.delete_json_file(json_display_vol_info_rest3)
       
        # Create an instance of c_ONTAPInfo_vol
        ontap_vol_info_handler = c_ONTAPInfo_vol()

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
                status = sys_db_run.run_ansible_playbook2(p_book_vol_info, result['stg_mgmt_ip'],json_display_vol_info_rest,conn)
                if status:
                    json_vol_info = sys_db_run.load_json(json_display_vol_info_rest)
                    json_vol_info2 = sys_db_run.load_json(json_display_vol_info_rest2)
                    json_vol_info3 = sys_db_run.load_json(json_display_vol_info_rest3)
   
 
                    if json_vol_info is None:
                        return 6  # Return error code 6 if JSON loading fails
                    # Remove volumes not in JSON
                    result = ontap_vol_info_handler.remove_volumes_not_in_json(conn, stg_uuid, json_vol_info)
                    if result != 0:
                        return result  # Return the error code from remove_volumes_not_in_json
                    # Insert or update SVM information into t_svms table
                    result = ontap_vol_info_handler.insert_or_update_vol_info(conn, stg_name, stg_uuid, json_vol_info, json_vol_info2,json_vol_info3)
                    if result != 0:
                        return result  # Return the error code from insert_or_update_aggregate_info
                    # update volumes_access_protocols
                    ontap_vol_info_handler.update_volumes_access_protocols(conn)
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

