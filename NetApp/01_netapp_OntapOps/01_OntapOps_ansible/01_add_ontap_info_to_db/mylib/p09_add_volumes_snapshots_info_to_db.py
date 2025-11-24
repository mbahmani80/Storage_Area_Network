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
vol_snapshot_info1_json = os.path.abspath("ymls/json/Display_volume_snapshot_info1_rest.json")
p_book_vol_snapshot_info = os.path.abspath("ymls/09_Display_volume_snapshot_information_rest.yml")

def format_elapsed_time(elapsed_time):
    if elapsed_time < 60:
        return f"{elapsed_time:.2f} seconds"
    else:
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        return f"{minutes} minutes and {seconds:.2f} seconds"

class c_ONTAPInfo_SnapshotManager:
    def __init__(self):
        self.snapshot_name = None
        self.snapshot_comment = None
        self.vol_name = None
        self.svm_name = None
        self.snapshot_create_time = None
        self.snapmirror_label = None
        self.stg_name = None
        self.stg_uuid_vserver_snap_create_time = None


    def format_datetime(self, datetime_str):
        try:
            dt_object = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt_object.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Error: Unable to parse datetime string '{datetime_str}'")
            return None

    def extract_info(self, stg_name, stg_uuid ,snapshot_data):
            self.snapshot_name = snapshot_data.get('snapshot')
            self.snapshot_comment = snapshot_data.get('comment') or None
            self.vol_name = snapshot_data.get('volume')
            self.svm_name = snapshot_data.get('vserver')
            self.snapshot_create_time = self.format_datetime(snapshot_data.get('create_time'))
            self.snapmirror_label = snapshot_data.get('snapmirror_label') or None
            self.stg_name = stg_name
            self.stg_uuid_vserver_snap_create_time =  ''.join([self.stg_name, self.svm_name, snapshot_data.get('create_time'),self.snapshot_name,stg_uuid])

    def delete_snapshot_records(self, conn, stg_name):
       try:
           cursor = conn.cursor(dictionary=True)
            
           r_query = """ 
                    DELETE FROM t_snapshots WHERE stg_name =  %s;
           """
           # Execute the query
           cursor.execute(r_query, (stg_name,))
   
           # Commit the transaction
           conn.commit()
    
           print(f"{cursor.rowcount} record(s) deleted.")
       except mysql.connector.Error as err:
           print(f"Error: {err}")
           #conn.rollback()
               



    def update_or_insert_snapshot(self, conn, stg_name, stg_uuid, json_snapshot_d1):
        try:
            cursor = conn.cursor(dictionary=True)
            for record in json_snapshot_d1['msg']['records']:
                self.extract_info(stg_name, stg_uuid, record)
                # self.print_vars()
                try:
                    
                    iu_query = """
                        INSERT INTO t_snapshots (
                                                 snapshot_name,
                                                 snapshot_comment,
                                                 vol_name,
                                                 svm_name,
                                                 snapshot_create_time,
                                                 snapmirror_label,
                                                 stg_name,
                                                 stg_uuid_vserver_snap_create_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            snapshot_name=VALUES(snapshot_name),
                            snapshot_comment=VALUES(snapshot_comment),
                            vol_name=VALUES(vol_name),
                            svm_name=VALUES(svm_name),
                            snapshot_create_time=VALUES(snapshot_create_time),
                            snapmirror_label=VALUES(snapmirror_label),
                            stg_name=VALUES(stg_name),
                            stg_uuid_vserver_snap_create_time=VALUES(stg_uuid_vserver_snap_create_time)
                    """
                    iu_values = (
                        self.snapshot_name, self.snapshot_comment, self.vol_name, self.svm_name,
                        self.snapshot_create_time, self.snapmirror_label, self.stg_name, self.stg_uuid_vserver_snap_create_time
                    )
                    cursor.execute(iu_query, iu_values)
                    conn.commit()
                    print(f"Record inserted or updated for snapshot {self.snapshot_name}")
                except mysql.connector.Error as err:
                    print("MySQL Error:", err)
                    return 3  # Return error code 3 for MySQL errors
                except Exception as e:
                    print("Required attributes are missing for insertion/update.")
                    print(f"An unexpected error occurred: {e}")
                    return 4  # Return error code 4 for other exceptions
            return 0  # Success
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return 4  # Return error code 4 for other exceptions
 

    def print_vars(self):
        print(f"self.stg_name: {self.stg_name}")
        print(f"self.stg_uuid_vserver_snap_create_time: {self.stg_uuid_vserver_snap_create_time}")
        print(f"self.snapshot_name: {self.snapshot_name}")
        print(f"self.snapshot_comment: {self.snapshot_comment}")
        print(f"self.vol_name: {self.vol_name}")
        print(f"self.svm_name: {self.svm_name}")
        print(f"self.snapshot_create_time: {self.snapshot_create_time}")
        print(f"self.snapmirror_label: {self.snapmirror_label}")



    
def main():
    try:
        start_time = time.time()  # Record the start time

        sys_db_run = c_SystemDBrunFunctions()
        conn = sys_db_run.connect_to_database()
        if not conn:
            return 5  # Return error code 5 if connection fails

        sys_db_run.delete_json_file(vol_snapshot_info1_json)

        snapshot_manager = c_ONTAPInfo_SnapshotManager()

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
            stg_uuid = result['stg_uuid']
            stg_ip = result['stg_mgmt_ip']
            print(f"Storage Name: {stg_name}, Management IP: {stg_ip}")

            if sys_db_run.check_ip_accessibility(stg_ip):
                #sql = f"SELECT v.stg_uuid, v.stg_name, v.svm_name FROM t_svms v JOIN t_stg_info s ON v.stg_name = s.stg_name WHERE s.stg_mgmt_ip = '{stg_ip}'  AND v.svm_state = 'running'"
                snapshot_manager.delete_snapshot_records(conn, stg_name)
                sql = f"SELECT v.stg_uuid, v.stg_name, v.svm_name FROM t_svms v JOIN t_stg_info s ON v.stg_name = s.stg_name WHERE s.stg_mgmt_ip = '{stg_ip}'"
                svm_list = sys_db_run.run_sql_query(conn, sql)
                for svm in svm_list:
                    svm_name = svm['svm_name']
                    stg_uuid_uuid = svm['stg_uuid']
                    stg_name = svm['stg_name']
                    print(f"stg_name: {stg_name}, svm_name: {svm_name}")

                    status = sys_db_run.run_ansible_playbook3(p_book_vol_snapshot_info, result['stg_mgmt_ip'], svm_name, vol_snapshot_info1_json, conn)
                    if status:
                        json_snapshot_d1 = sys_db_run.load_json(vol_snapshot_info1_json)

                        if json_snapshot_d1 is None:
                            print("Error: Unable to load JSON files.")
                            return
                        else:
                            snapshot_manager.update_or_insert_snapshot(conn, stg_name, stg_uuid,  json_snapshot_d1)

        conn.close()

        sys_db_run.delete_json_file(vol_snapshot_info1_json)
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        readable_time = format_elapsed_time(elapsed_time)  # Format the elapsed time
        print(f"Script executed in {readable_time}.")  # Print the formatted elapsed time

    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return 3  # Return error code 3 for MySQL errors

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 4  # Return error code 4 for other exceptions

if __name__ == "__main__":
    main()

