import os
import sys
import datetime
import json
import subprocess
import mysql.connector
import re
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta


vars_files=os.path.abspath("ymls/vars.yml")

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project_directory)
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path
sys.path.append(parent_dir)


class LogManager:
    def __init__(self, log_file_base):
        self.log_file_base = log_file_base
        self.directory, self.base_name = os.path.split(log_file_base)

    def update_log(self, message):
        # Ensure the directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Get the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Define the log file name with the current date
        log_file = os.path.join(self.directory, f"{self.base_name}_{current_date}.txt")

        # Format the log entry
        log_entry = f"{current_time} - {message}\n"

        # Open the log file in append mode and write the log entry
        with open(log_file, 'a') as file:
            file.write(log_entry)

    def zip_old_logs(self):
        # Define the zip file name
        zip_file_name = os.path.join(self.directory, f"{self.base_name}_logs.zip")

        # Ensure the directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Calculate the date 7 days ago
        seven_days_ago = datetime.now() - timedelta(days=7)

        # Create a zip file
        with zipfile.ZipFile(zip_file_name, 'a') as zipf:
            # Iterate over all files in the directory
            for file_name in os.listdir(self.directory):
                # Check if the file matches the base name and is older than 7 days
                if file_name.startswith(self.base_name) and file_name.endswith('.txt'):
                    file_date_str = file_name[len(self.base_name) + 1:-4]
                    file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                    if file_date < seven_days_ago:
                        # Add the file to the zip archive
                        zipf.write(os.path.join(self.directory, file_name), file_name)
                        # Optionally, delete the original log file after zipping
                        os.remove(os.path.join(self.directory, file_name))


class c_SystemDBrunFunctions:
    #def __init__(self, host="localhost", user="admin1", password="Admin123", database="ontapdb1",vars_files="ymls/vars.yml"):
    def __init__(self, vars_files=os.path.abspath('./ymls/vars.yml')):
        self.host = "localhost" 
        self.user = "admin1"
        self.password = "Admin123"
        self.database = "ontapdb1"
        self.yml_files = []
        self.vars_files = vars_files



    # Function to copy the appropriate YAML file based on customer ID
    def copy_var_yaml_file(self, customer_id):
        # Get the source file name based on customer ID
        source_file = self.customer_files.get(customer_id)

        if not source_file:
            print(f"No YAML file found for customer ID: {customer_id}")
            return

        # Define the destination file path
        destination_file = self.customer_files.get(0)
        try:
            # Copy the source file to the destination
            shutil.copy2(source_file, destination_file)
            print(f"Copied {source_file} to {destination_file}")
        except FileNotFoundError:
            print(f"File {source_file} not found")
        except Exception as e:
            print(f"An error occurred: {e}")


    def connect_to_database(self):
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            return None

    # Method to run a sql query
    def run_sql_query(self, conn, sql):
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                if sql.lower().startswith("select"):
                    # Fetch data for SELECT queries
                    data = cursor.fetchall()
                    return data
                else:
                    # Commit for INSERT, UPDATE, DELETE queries
                    conn.commit()
                    return {"message": "Query executed successfully."}
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            return None


    def check_ip_accessibility(self, ip_address):
        try:
            # Pinging the IP address
            response = subprocess.run(['ping', '-c', '1', ip_address], stdout=subprocess.PIPE)
            # Checking the response
            if response.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def get_and_validate_ips(self):
        input_ips = input("Enter comma-separated IP addresses: ")
        ip_list = input_ips.split(',')
        valid_ips = []
        invalid_ips = []

        # Regular expression for validating an IP address
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')

        for ip in ip_list:
            ip = ip.strip()
            if ip_pattern.match(ip):
                valid_ips.append(ip)
            else:
                invalid_ips.append(ip)

        return valid_ips, invalid_ips

    def process_ips(self):
        valid_ips, invalid_ips = self.get_and_validate_ips()

        for ip in valid_ips:
            if self.check_ip_accessibility(ip):
                print(f"The IP address {ip} is accessible.")
            else:
                print(f"The IP address {ip} is not accessible.")

        for ip in invalid_ips:
            print(f"The IP address {ip} is not in the correct format.")

        return valid_ips

    def load_json(self,file_path):
        try:
            with open(file_path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON file '{file_path}': {e}")
            return None
        except Exception as e:
            print(f"Error: An unexpected error occurred while loading JSON file '{file_path}': {e}")
            return None

    def run_ansible_playbook(self, playbook_path, extra_vars):
        command = ["ansible-playbook", playbook_path, "--extra-vars", extra_vars]
        try:
            subprocess.run(command, check=True)
            print("Playbook executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing playbook: {e}")

    def create_vars_file(self, stg_usr_pass_data):
        vars_file_path = self.vars_files 
        with open(vars_file_path, 'w') as vars_file:
            vars_file.write("---\n")
            vars_file.write(f"user: {stg_usr_pass_data['username']}\n")
            vars_file.write(f"pass: !vault |\n")
            vars_file.write(f"          {stg_usr_pass_data['password']}\n")
            vars_file.write("https: true\n")
            vars_file.write("validate_certs: false\n")
            vars_file.write("\n")
            vars_file.write("login:\n")
            vars_file.write(f"  hostname: \"{{{{ storageip }}}}\"\n")
            vars_file.write(f"  username: \"{{{{ user }}}}\"\n")
            vars_file.write(f"  password: \"{{{{ pass }}}}\"\n")
            vars_file.write("  https: true\n")
            vars_file.write("  validate_certs: false\n")

    def run_ansible_playbook2(self, playbook_path, stgip, json_file_path, conn):
        # Change directory to the playbook's directory
        playbook_dir = os.path.dirname(playbook_path)
        os.chdir(playbook_dir)
        sql = f"SELECT storageip, username, password, enabled FROM t_stg_access_data WHERE storageip = '{stgip}'"
        stg_list = self.run_sql_query(conn, sql)
        if stg_list:
            for stg in stg_list:
                stg_ip = stg['storageip']
                stg_username = stg['username']
                stg_password = stg['password']
                stg_enabled = stg['enabled']
                print(f"stg_ip: {stg_ip}, stg_enabled: {stg_enabled}")
            if stg_enabled:

                # Create the vars.yml file with the host data
                self.create_vars_file(stg)
        
                # Construct the extra_vars argument as a JSON string
                extra_vars = {
                    "storageip": stg_ip,
                    "output_file": json_file_path,
                }
                extra_vars_arg = json.dumps(extra_vars)
        
                # Construct the command to run the playbook
                command = [
                    "ansible-playbook",
                    os.path.basename(playbook_path),  # Use only the playbook file name
                    "--extra-vars",
                    extra_vars_arg
                ]
        
                # Execute the command
                try:
                    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print("Playbook executed successfully.")
                    print(result.stdout)
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"Error executing playbook: {e}")
                    print(e.stderr)
                    return False
            else:
                print("storage in db is not enabled. That is why it is not processed. Run program p100_insert_stg_access_data_to_db.py if needed")
                return False
        
    def run_ansible_playbook3(self, playbook_path, stgip, svm, json_f1_path, conn):
        # Change directory to the playbook's directory
        playbook_dir = os.path.dirname(playbook_path)
        os.chdir(playbook_dir)

        sql = f"SELECT storageip, username, password, enabled FROM t_stg_access_data WHERE storageip = '{stgip}'"
        stg_list = self.run_sql_query(conn, sql)
        if stg_list:
            for stg in stg_list:
                stg_ip = stg['storageip']
                stg_username = stg['username']
                stg_password = stg['password']
                stg_enabled = stg['enabled']
                print(f"stg_ip: {stg_ip}, stg_enabled: {stg_enabled}")
            if stg_enabled:

                # Create the vars.yml file with the host data
                self.create_vars_file(stg)
                # Construct the extra_vars argument as a JSON string
                extra_vars = {
                    "storageip": stg_ip,
                    "output_file1": json_f1_path,
                    "svm":svm
                }
                extra_vars_arg = json.dumps(extra_vars)
        
                # Construct the command to run the playbook
                command = [
                    "ansible-playbook",
                    os.path.basename(playbook_path),  # Use only the playbook file name
                    "--extra-vars",
                    extra_vars_arg
                ]
        
                # Execute the command
                try:
                    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print("Playbook executed successfully.")
                    print(result.stdout)
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"Error executing playbook: {e}")
                    print(e.stderr)
                    return False
            else:
                print("storage in db is not enabled. That is why it is not processed. Run program p100_insert_stg_access_data_to_db.py if needed")
                return False

    def delete_json_file(self, file_path):
        """Delete a specific JSON file."""
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted JSON file: {file_path}")
            else:
                print(f"No JSON file found at: {file_path}")
        except Exception as e:
            print(f"An error occurred while deleting JSON file: {e}")


# Main function
def main():
    sys_db_run = c_SystemDBrunFunctions(vars_files)
    conn = sys_db_run.connect_to_database()
    #valid_ips = sys_db_run.process_ips()

    sql = "SELECT stg_name, stg_uuid, stg_mgmt_ip FROM t_stg_info"
    results_list = sys_db_run.run_sql_query(conn,sql)
    print("SELECT query result:", results_list)

    #extra_vars = f"storageip={stgip} output_file='{output_file}'"
    #sys_db_run.run_ansible_playbook(p_book_ontap_info, extra_vars)
    #p_book_ontap_info = os.path.abspath("ymls/01_Display_ontap_info_rest.yml")
    #p_book_ontap_metrocluster_info = os.path.abspath("ymls/02_Display_ontap_metrocluster_info_rest.yml")
    #json_display_ontap_info_rest = os.path.abspath("ymls/json/Display_ontap_info_rest.json")
    #json_display_ontap_metrocluster_info_rest = os.path.abspath("ymls/json/Display_ontap_metrocluster_info_rest.json")
    #for stgip in valid_ips:
    #    sys_db_run.run_ansible_playbook2(p_book_ontap_metrocluster_info, stgip, json_display_ontap_metrocluster_info_rest)

    #stgip = '192.168.178.4'  # Replace with the IP address you want to process
    valid_ips = sys_db_run.process_ips()
    for stgip in valid_ips:
        if sys_db_run.check_ip_accessibility(stgip):
            json_file_path = os.path.abspath('ymls/json/test.json')  # Path to the vars.yml file
            playbook_path = os.path.abspath('ymls/01_Display_ontap_info_rest.yml')  # Replace with the actual playbook path
            status = sys_db_run.run_ansible_playbook2(playbook_path, stgip, json_file_path, conn)
            if status:
                print("status is ok")

if __name__ == "__main__":
    main()

