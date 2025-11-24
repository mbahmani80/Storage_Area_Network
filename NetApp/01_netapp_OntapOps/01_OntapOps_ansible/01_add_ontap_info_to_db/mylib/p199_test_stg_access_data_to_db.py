import mysql.connector
import subprocess
import os
import sys
import json

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project_directory)
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path
sys.path.append(parent_dir)

def get_sql_host_data(ip_address):
    # Connect to the database
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='admin1',
        password='Admin123',
        database='ontapdb1'
    )
    cursor = conn.cursor(dictionary=True)

    # Fetch the details for the specified IP address
    query = "SELECT storageip, username, password FROM t_stg_access_data WHERE storageip = %s"
    cursor.execute(query, (ip_address,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def create_vars_file(sql_host_data):
    vars_file_path = os.path.abspath("ymls/vars.yml")
    with open(vars_file_path, 'w') as vars_file:
        vars_file.write("---\n")
        vars_file.write(f"user: {sql_host_data['username']}\n")
        vars_file.write(f"pass: !vault |\n")
        vars_file.write(f"          {sql_host_data['password']}\n")
        vars_file.write("https: true\n")
        vars_file.write("validate_certs: false\n")
        vars_file.write("\n")
        vars_file.write("login:\n")
        vars_file.write(f"  hostname: \"{{{{ storageip }}}}\"\n")
        vars_file.write(f"  username: \"{{{{ user }}}}\"\n")
        vars_file.write(f"  password: \"{{{{ pass }}}}\"\n")
        vars_file.write("  https: true\n")
        vars_file.write("  validate_certs: false\n")

def run_ansible_playbook(playbook_path, ip_address,sql_host_data):
    # Fetch the host data from the database
    if not sql_host_data:
        print(f"No data found for IP address: {ip_address}")
        return

    # Create the vars.yml file with the host data
    create_vars_file(sql_host_data)

    # Construct the extra_vars argument as a JSON string
    extra_vars = {
        "storageip": sql_host_data['storageip'],
        "output_file": os.path.abspath("ymls/json/file.json")
    }
    extra_vars_arg = json.dumps(extra_vars)

    # Construct the command to run the playbook
    command = [
        "ansible-playbook",
        playbook_path,  # Use only the playbook file name
        "--extra-vars",
        extra_vars_arg
    ]

    # Execute the command
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        #result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Playbook executed successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing playbook: {e}")
        print(e.stderr)

# Example usage
#ip_address = '192.168.178.4'  # Replace with the IP address you want to process
ip_address = '172.17.100.200'  # Replace with the IP address you want to process
vars_file_path = os.path.abspath('ymls/vars.yml')  # Path to the vars.yml file
#playbook_path = os.path.abspath('ymls/11_Display_ontap_svm_peer_info_rest.yml')  # Replace with the actual playbook path
playbook_path = os.path.abspath('ymls/07_Display_svm_peer_info_rest.yml')  # Replace with the actual playbook path

sql_host_data = get_sql_host_data(ip_address)
run_ansible_playbook(playbook_path, ip_address, sql_host_data)

