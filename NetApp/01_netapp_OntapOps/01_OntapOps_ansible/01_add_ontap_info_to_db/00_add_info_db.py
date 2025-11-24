import argparse
import os
import subprocess
import json
import sys
import mysql.connector
from mylib import p00_tools_functions
from mylib.p00_tools_functions import c_SystemDBrunFunctions
from mylib.p00_tools_functions import LogManager
from mylib import p01_add_customer_to_db
from mylib.p01_add_customer_to_db import c_CustomerManager
from mylib import p02_add_datacenters_to_db
from mylib.p02_add_datacenters_to_db import c_DatacenterManager
from mylib import p03_add_ontap_info_to_db
from mylib.p03_add_ontap_info_to_db import c_ONTAPInfo
from mylib import p04_add_ontap_peer_info_to_db 
from mylib.p04_add_ontap_peer_info_to_db import c_ONTAPInfo_peer
from mylib import p05_add_ontap_node_info_to_db
from mylib.p05_add_ontap_node_info_to_db import c_ONTAPInfo_node
from mylib import p06_add_aggregates_info_to_db
from mylib import p07_add_svm_info_to_db
from mylib import p08_add_volumes_info_to_db
from mylib import p198_insert_stg_login_data_to_db
from mylib.p198_insert_stg_login_data_to_db import c_OntapLoginData 

# pip3 install mysql-connector-python 

# Define the files path
vault_password_file='/home/ubuntu/01_lab/vault_password_file'
log_file_path = os.path.abspath("log/p03_add_ontap_info")
vars_files=os.path.abspath("mylib/ymls/vars.yml")
json_customer_data_ids_file_path = "mylib/ymls/json/customer_data_ids.json"

# Define the files path for c_ONTAPInfo class
json_customer_data_ids_file_path = os.path.abspath("mylib/ymls/json/customer_data_ids.json")
json_display_ontap_info_rest = os.path.abspath("mylib/ymls/json/Display_ontap_info_rest.json")
json_display_ontap_metrocluster_info_rest = os.path.abspath("mylib/ymls/json/Display_ontap_metrocluster_info_rest.json")
p_book_ontap_info = os.path.abspath("mylib/ymls/01_Display_ontap_info_rest.yml")
p_book_ontap_metrocluster_info = os.path.abspath("mylib/ymls/02_Display_ontap_metrocluster_info_rest.yml")

# Define the files path for c_ONTAPInfo_peer
json_display_ontap_cluster_peer_info_rest = os.path.abspath("mylib/ymls/json/Display_ontap_cluster_peer_info_rest.json")
p_book_ontap_cluster_peers_info_rest = os.path.abspath("mylib/ymls/03_Display_ontap_cluster_peers_info_rest.yml")

# Function to parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Add information to the database")
    parser.add_argument("-m", "--menu", action="store_true", help="Use menu-based approach")
    parser.add_argument("-a", "--add-customer", action="store_true", help="Add customer")
    parser.add_argument("-d", "--add-datacenters", action="store_true", help="Add datacenter")
    parser.add_argument("-p", "--add-credential", action="store_true", help="Add credential")
    parser.add_argument("-c", "--add-cluster", action="store_true", help="Add a cluster or Metrocluster")
    parser.add_argument("-u", "--update-cluster", action="store_true", help="Update cluster info")
    return parser.parse_args()

# function to add customer
def f_add_customer(conn,customer_manager):

    try:
        if not conn:
            sys.exit(1)

        customer_manager.run_user_interface()

        conn.close()
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return 1

# function to add datacenters
def f_add_datacenters(conn,dc_manager):

    dc_manager.run_user_interface()

def f_add_credential(conn,pass_manager):

    if conn:
        while True:
            pass_manager.show_menu()
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                pass_manager.show_storage(conn)
            elif choice == '2':
                data = pass_manager.get_user_input(conn)
                pass_manager.insert_data(conn, data)
            elif choice == '3':
                pass_manager.show_storage(conn)
                ips = input("Enter comma-separated storage IPs to enable: ").strip()
                pass_manager.update_storage_status(conn, ips, enable=True)
            elif choice == '4':
                pass_manager.show_storage(conn)
                ips = input("Enter comma-separated storage IPs to disable: ").strip()
                pass_manager.update_storage_status(conn, ips, enable=False)
            elif choice == '5':
                pass_manager.update_All_storage_status(conn, enable=True)
                pass_manager.show_storage(conn)
            elif choice == '6':
                pass_manager.update_All_storage_status(conn, enable=False)
                pass_manager.show_storage(conn)
            elif choice == '7':
                pass_manager.show_storage(conn)
                ips = input("Enter comma-separated storage IPs to delete login infos: ").strip()
                pass_manager.delete_storage(conn, ips)
            elif choice == 'x':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please try again.")

        conn.close()
 




# function to add cluster
def f_add_cluster(conn,sys_db_run,dc_manager):

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



# function to add/update ONTAPInfo_peer
def f_add_update_ONTAPInfo_peer(conn,sys_db_run,ontap_info_peer):

    sys_db_run.delete_json_file(json_display_ontap_cluster_peer_info_rest)

    # Print each field from the query
    sql = "SELECT t_stg_info.stg_name,t_stg_info.stg_uuid,t_stg_info.stg_mgmt_ip,t_stg_info.customer_id FROM t_stg_info JOIN t_stg_access_data ON t_stg_info.stg_mgmt_ip = t_stg_access_data.storageip WHERE t_stg_access_data.enabled = 1"

    results_list = sys_db_run.run_sql_query(conn,sql)
    for result in results_list:
        print(f"Storage Name: {result['stg_name']}, UUID: {result['stg_uuid']}, Management IP: {result['stg_mgmt_ip']}, customer_id: {result['customer_id']}")
        if sys_db_run.check_ip_accessibility(result['stg_mgmt_ip']):

            status = sys_db_run.run_ansible_playbook2(p_book_ontap_cluster_peers_info_rest,result['stg_mgmt_ip'],json_display_ontap_cluster_peer_info_rest,conn )
            if status:
                json_ontap_cluster_peer_info = sys_db_run.load_json(json_display_ontap_cluster_peer_info_rest)
                ontap_info_peer.ontap_peer_info_process_records(conn, result['stg_name'],result['stg_uuid'],result['customer_id'], json_ontap_cluster_peer_info)

    # Close database connection
    conn.close()
    


# function to add nodes of cluster
def f_add_nodes(conn):

    # Create an instance of c_ONTAPInfo_node
    ontap_node_info_handler = c_ONTAPInfo_node(json_customer_data_ids_file_path, json_display_ontap_info_rest,
                                                    json_display_ontap_node_info_rest)
    # Fetch stg_uuid from the other JSON file
    stg_uuid = ontap_node_info_handler.fetch_stg_uuid_from_json()

    # Fetch customer_id and datacenter_id
    customer_id, datacenter_id = ontap_node_info_handler.fetch_ids_from_json()


    # Fetch node information from the JSON file
    node_info = ontap_node_info_handler.fetch_node_info_from_json()

    # If any of the required data is missing, exit with error
    if None in [stg_uuid, customer_id, datacenter_id] or not node_info:
        print("Error: Missing required data.")
        return 1

    # Insert or update node information into t_stg_node_info table
    result_write = p05_add_ontap_node_info_to_db.insert_or_update_ontap_node_info(conn, node_info, stg_uuid, customer_id, datacenter_id)
    if result_write != 0:
        return result_write


def f_add_aggregates(conn):

    aggregate_info = p06_add_aggregates_info_to_db.load_json(json_display_aggregates_info_rest)
    if aggregate_info is None:
        return 6  # Return error code 6 if JSON loading fails

    # Insert or update aggregate information into t_aggregates table
    result = p06_add_aggregates_info_to_db.insert_or_update_aggregate_info(conn, aggregate_info)
    if result != 0:
        return result  # Return the error code from insert_or_update_aggregate_info

def f_add_svms(conn):
    svm_info = p07_add_svm_info_to_db.load_json(json_display_svm_info_rest)

    # Insert or update SVM information into t_svms table
    p07_add_svm_info_to_db.insert_or_update_svm_info(conn, svm_info)

    return 0

def f_add_vols(conn):

    json_data = p08_add_volumes_info_to_db.load_json(json_display_volume_information_rest)
    volumes = json_data['ontap_info']['storage/volumes']['records']

    if volumes:
        success = p08_add_volumes_info_to_db.update_or_insert_volume_info(conn, volumes)
        if success:
            print("All volume information updated or inserted successfully!")
        else:
            print("Failed to update or insert volume information.")

    return 0

# Main function for menu-based approach
def menu_based(conn,sys_db_run,stgip,customer_manager,dc_manager,pass_manager):
    while True:
        print("\nMenu:")
        print("1. Add customer")
        print("2. Add datacenter")
        print("3. Add credential")
        print("4. Add a cluster or Metrocluster")
        print("5. Update cluster info")
        print("x. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            f_add_customer(conn,customer_manager)
        elif choice == "2":
            f_add_datacenters(conn,dc_manager)
        elif choice == "3":
            f_add_credential(conn, pass_manager) 
        elif choice == "4":
            f_add_cluster(conn,sys_db_run,dc_manager)
            f_add_update_ONTAPInfo_peer(conn,sys_db_run,ontap_info_peer)
        elif choice == "5":
            f_add_update_ONTAPInfo_peer(conn,sys_db_run,ontap_info_peer)
        elif choice == "x":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


# Function to display usage information
def usage():
    print("Usage: python 00_add_info_db.py [-m | -a | -d | -p | -c | -u]")
    print("Options:")
    print("  -m, --menu            : Use menu-based approach")
    print("  -a, --add-customer    : Add customer")
    print("  -d, --add-datacenters : Add datacenter")
    print("  -p, --add-credential  : Add credential")
    print("  -c, --add-cluster     : Add a cluster or Metrocluster")
    print("  -u, --update-cluster-info : Update cluster info")

# Main function
def main():
    args = parse_args()

    # Connect to the MariaDB database
    sys_db_run = c_SystemDBrunFunctions(vars_files)
    try:
        conn = sys_db_run.connect_to_database()

        #sys_db_run.delete_json_files()
        if not conn:
            return 1  # Return error code 1 if connection fails

        # Create CustomerManager and customer_manager instance
        customer_manager = c_CustomerManager(conn)
        dc_manager = c_DatacenterManager(conn, customer_manager)
        # Create pass_manager instance
        pass_manager = c_OntapLoginData(vault_password_file)  
        # Create ontap_info_peer instance
        ontap_info_peer = c_ONTAPInfo_peer()
    

        if args.menu:
            menu_based(conn,sys_db_run,stgip,customer_manager,dc_manager,pass_manager)
        elif args.add_customer:
            f_add_customer(conn,customer_manager)
        elif args.add_datacenters:
            f_add_datacenters(conn,dc_manager)
        elif args.add_credential:
            f_add_credential(conn,pass_manager)
        elif args.add_cluster:
            f_add_cluster(conn,sys_db_run,dc_manager)
            f_add_update_ONTAPInfo_peer(conn,sys_db_run,ontap_info_peer)
        elif args.update_cluster:
            f_add_update_ONTAPInfo_peer(conn,sys_db_run,ontap_info_peer)
        else:
            usage()
    
        # Close database connection
        conn.close()

    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return 1
if __name__ == "__main__":
    main()

