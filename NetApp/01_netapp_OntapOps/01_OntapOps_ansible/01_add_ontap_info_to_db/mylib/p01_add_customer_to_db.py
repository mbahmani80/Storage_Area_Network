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

class c_CustomerManager:
    def __init__(self, conn):
        self.conn = conn

    def list_customers(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM t_customer")
            customers = cursor.fetchall()
            return customers
        except Error as e:
            print(f"Error retrieving customers: {e}")
            return []

    # Function to get customer input
    def get_customer_input(self):
        customer_name = input("Enter customer name: ")
        customer_email = input("Enter customer email: ")
        customer_address = input("Enter customer address: ")
    
        customer_input = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_address": customer_address
        }
    
        return customer_input
    
    # Function to insert data into t_customer table
    def insert_customer(self, customer_data):
        try:
            cursor = self.conn.cursor()
            isql = """INSERT INTO t_customer 
                       (customer_name, customer_email, customer_address)
                      VALUES (%s, %s, %s)
                   """
            ivalues = (customer_data["customer_name"], customer_data["customer_email"], customer_data["customer_address"])

            cursor.execute(isql,ivalues)
            self.conn.commit()
            print("Customer information inserted successfully.")
            return 0
        except mysql.connector.Error as err:
            print(f"Error inserting customer information: {err}")
            return 1
    
    def get_input_data(self, current_data):
        new_data = {}
        print("Enter new customer information (press enter to accept current value):")
        new_data['customer_name'] = input(f"Name (current: {current_data[1]}): ") or current_data[1]
        new_data['customer_email'] = input(f"Email (current: {current_data[2]}): ") or current_data[2]
        new_data['customer_address'] = input(f"Address (current: {current_data[3]}): ") or current_data[3]
        return new_data

    def update_customer(self, customer_id, new_data):
        try:
            cursor = self.conn.cursor()
            self.conn.commit()
            usql = """ UPDATE t_customer 
                       SET customer_name = %s, customer_email = %s, customer_address = %s 
                       WHERE customer_id = %s"""
            uvalues = (new_data['customer_name'], new_data['customer_email'], new_data['customer_address'], customer_id)
 
            cursor.execute(usql,uvalues)
            self.conn.commit()
            print("Customer updated successfully")
        except Error as e:
            self.conn.rollback()
            print(f"Error updating customer: {e}")

        # Update related fields in other tables
        self.conn.commit()

    def show_customers_and_select(self):
        try:
            customers = self.list_customers()
            # Get customer choice
            print("List of Customers:")
            for customer in customers:
                print(customer)
            
            customer_id = int(input("Enter the customer ID: "))
            selected_customer = None
            for cust in customers:
                if cust[0] == customer_id:
                    selected_customer = cust
                    break       
            if selected_customer:
                print(f"You have selected: {selected_customer}")
                return selected_customer
            else:
                print("No customer found with the given ID.")
                return None
        except Error as e:
            print(f"An error occurred: {e}")
        except ValueError:
            print("Invalid input. Please enter a numeric customer ID.")


    def run_user_interface(self):
        while True:
            # Present the options to the user
            print("======================== ")
            print(" CustomerManager:")
            print("  1. List customers info")
            print("  2. Insert a customer info")
            print("  3. update a customer info")
            print("  4. Delete a customer info")
            print("  x. Exit")
            print("======================== ")
        
            # Get the user's choice
            user_choice = input("Enter your choice: ")
            
            # Perform the action based on the user's choice
            if user_choice == "1":
                # List current customers
                customers = self.list_customers()
                print("Current Customers:")
                for customer in customers:
                    print(customer)
                
            elif user_choice == "2":
                # Code to insert a new customer would go here
                print("You have chosen to insert a new customer.")

                # Get customer input
                customer_data = self.get_customer_input()
        
                # Insert customer data into t_customer table
                result = self.insert_customer(customer_data)
        
            elif user_choice == "3":
                selected_customer = self.show_customers_and_select()
                if selected_customer:
                    customer_id = selected_customer[0] 
                    new_data = self.get_input_data(selected_customer)
                    self.update_customer(customer_id, new_data)
            elif user_choice == "4":
                print("Not yet implemented!")
            elif user_choice == "x":
                print("Exiting...")
                #exit(0)
                break
            else:
                print("Invalid choice. Please enter 1 to 4 or x.")
        

def main():
    sys_db_run = c_SystemDBrunFunctions()
    try:
        conn = sys_db_run.connect_to_database()
        if not conn:
            sys.exit(1)

        customer_manager = c_CustomerManager(conn)
        customer_manager.run_user_interface()

        conn.close()
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return 1

if __name__ == "__main__":
    main()



