import os
import sys
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

from mylib import p01_add_customer_to_db 
from mylib.p01_add_customer_to_db import c_CustomerManager

class c_DatacenterManager:
    def __init__(self, conn, o_c_CustomerManager):
        self.conn = conn
        self.customer_manager = o_c_CustomerManager

    def list_datacenters(self):
        try:
            # Get customer choice
            selected_customer = self.customer_manager.show_customers_and_select()
            if selected_customer:
                customer_id = selected_customer[0] 
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM t_datacenters WHERE customer_id = %s", (customer_id,))
                datacenters = cursor.fetchall()
                return datacenters
        except Error as e:
            print(f"Error retrieving datacenters: {e}")
            return []

    # Function to get datacenter input
    def get_datacenter_input(self):
        datacenter_name = input("Enter datacenter name: ")
        datacenter_country = input("Enter datacenter country code (e.g., 'DE' for Germany): ")
        datacenter_city = input("Enter datacenter city: ")
        datacenter_address = input("Enter datacenter address: ")
    
        datacenter_input = {
            "datacenter_name": datacenter_name,
            "datacenter_country": datacenter_country,
            "datacenter_city": datacenter_city,
            "datacenter_address": datacenter_address
        }
        
        return datacenter_input
        
    
    # Function to insert datacenter into into t_datacenters table
    def insert_datacenter(self, conn, datacenter_data, customer_id):
    
        try:
            cursor = conn.cursor()
            isql = """INSERT INTO t_datacenters
                             (datacenter_name, datacenter_country, datacenter_city, datacenter_address, customer_id)
                       VALUES (%s, %s, %s, %s, %s)
                   """
            ivalue = (datacenter_data["datacenter_name"], 
                      datacenter_data["datacenter_country"], 
                      datacenter_data["datacenter_city"], 
                      datacenter_data["datacenter_address"], 
                      customer_id)

            cursor.execute(isql,ivalue)
            conn.commit()
            print("Datacenter information inserted successfully.")
            return 0
        except mysql.connector.Error as err:
            print(f"Error inserting datacenter information: {err}")
            return 1

    def get_input_data(self, current_data):
        new_data = {}
        print("Enter new Datacenter information (press enter to accept current value):")
        new_data['datacenter_name'] = input(f"Name (current: {current_data[1]}): ") or current_data[1]
        new_data['datacenter_country'] = input(f"Country (current: {current_data[4]}): ") or current_data[4]
        new_data['datacenter_city'] = input(f"City (current: {current_data[2]}): ") or current_data[2]
        new_data['datacenter_address'] = input(f"Address (current: {current_data[5]}): ") or current_data[5]

        return new_data
    
    # Function to update datacenter info into t_datacenters table
    def update_datacenter(self, datacenter_id, new_data):
    
        try:
            cursor = self.conn.cursor()
            usql = """UPDATE t_datacenters
                      SET datacenter_name = %s, datacenter_country = %s, datacenter_city = %s, datacenter_address = %s
                      WHERE datacenter_id = %s"""
                   
            uvalue = (new_data['datacenter_name'], 
                      new_data["datacenter_country"], 
                      new_data["datacenter_city"], 
                      new_data["datacenter_address"], 
                      datacenter_id)

            cursor.execute(usql,uvalue)
            self.conn.commit()
            print("Datacenter information updated successfully.")
            return 0
        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"Error updated datacenter information: {err}")
            return 1
        # Update related fields in other tables
        self.conn.commit()

        
    def show_datacenter_and_select(self):
        try:
            datacenters = self.list_datacenters()
            # Get datacenter choice
            print("List of Datacenter:")
            for datacenter in datacenters:
                print(datacenter)
            
            datacenter_id = int(input("Enter the datacenter ID: "))
            selected_datacenter = None
            for dc in datacenters:
                if dc[0] == datacenter_id:
                    selected_datacenter = dc
                    break       
            if selected_datacenter:
                print(f"You have selected: {selected_datacenter}")
                return selected_datacenter
            else:
                print("No datacenter found with the given ID.")
                return None
        except Error as e:
            print(f"An error occurred: {e}")
        except ValueError:
            print("Invalid input. Please enter a numeric datacenter ID.")

    def run_user_interface(self):
        while True:
            # Present the options to the user
            print("======================== ")
            print(" Datacenter Manager:")
            print("  1. List datacenter info")
            print("  2. Insert a datacenter info")
            print("  3. update a datacenter info")
            print("  4. Delete a datacenter info")
            print("  x. Exit")
            print("======================== ")
        
            # Get the user's choice
            user_choice = input("Enter your choice: ")
            
            # Perform the action based on the user's choice
            if user_choice == "1":
                # List current datacenter
                datacenters = self.list_datacenters()
                print("Current Datacenters:")
                for datacenter in datacenters:
                    print("------------------------") 
                    print(datacenter)
                
            elif user_choice == "2":
                # Code to insert a new customer would go here
                print("You have chosen to insert a new datacenter.")
                try:    
            
                    # Get customer choice
                    selected_customer = self.customer_manager.show_customers_and_select()
                    if selected_customer:
                        customer_id = selected_customer[0] 
                        # Get datacenter input
                        datacenter_data = self.get_datacenter_input()
                        # Insert datacenter data into t_datacenters table
                        result = self.insert_datacenter(self.conn, datacenter_data, customer_id)
                    else: 
                        print("Customer ID does not exist. Please try again.")
            
                except ValueError:
                    print("Invalid input. Please enter a valid customer ID.")
                except mysql.connector.Error as err:
                    print(f"Database connection error: {err}")
                    return 1

            elif user_choice == "3":
                selected_datacenter = self.show_datacenter_and_select()
                print("------------------------")
                print(selected_datacenter)
                if selected_datacenter:
                    datacenter_id = selected_datacenter[0] 
                    new_data = self.get_input_data(selected_datacenter)
                    self.update_datacenter(datacenter_id, new_data)
            elif user_choice == "4":
                print("Not yet implemented!")
            elif user_choice == "x":
                print("Exiting...")
                #exit(0)
                break
            else:
                print("Invalid choice. Please enter 1 to 4 or x.")
        


# Main function
def main():
    # Connect to the database
    sys_db_run = c_SystemDBrunFunctions()
    # Connect to the MariaDB database
    conn = sys_db_run.connect_to_database()
    if not conn:
        return 1  # Return error code 1 if connection fails

    # Create CustomerManager instance
    customer_manager = c_CustomerManager(conn)
    dc_manager = c_DatacenterManager(conn, customer_manager)

    dc_manager.run_user_interface()

    conn.close()

if __name__ == "__main__":
    sys.exit(main())

