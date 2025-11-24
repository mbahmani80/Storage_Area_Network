#  pip3 install pyvis
import mysql.connector

# Function to fetch data from the database
def fetch_data(query):
    connection = mysql.connector.connect(
        host="localhost",
        user="admin1",
        password="Admin123",
        database="ontapdb1"
    )
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data

# Function to generate network diagram HTML content
def generate_network_html():
    # Fetch data from tables to create diagram
    customers = fetch_data("SELECT * FROM t_customer")
    datacenters = fetch_data("SELECT * FROM t_datacenters")
    stg_info = fetch_data("SELECT * FROM t_stg_info")
    stg_node_info = fetch_data("SELECT * FROM t_stg_node_info")
    aggregates = fetch_data("SELECT * FROM t_aggregates")
    svms = fetch_data("SELECT * FROM t_svms")
    volumes = fetch_data("SELECT * FROM t_volumes")
    snapshots = fetch_data("SELECT * FROM t_snapshots")

    # Construct HTML content for network diagram
    html_content = "<html><head><title>Network Diagram</title></head><body>"
    html_content += "<h1>Network Diagram</h1>"
    html_content += "<ul>"
    for customer in customers:
        html_content += f"<li>Customer: {customer[1]}</li>"
    for datacenter in datacenters:
        html_content += f"<li>Datacenter: {datacenter[1]}</li>"
    # Add other entities as needed
    html_content += "</ul>"
    html_content += "</body></html>"

    # Save HTML content to a file
    with open("netapp_storage_diagram.html", "w") as file:
        file.write(html_content)

# Main function
def main():
    generate_network_html()

if __name__ == "__main__":
    main()

