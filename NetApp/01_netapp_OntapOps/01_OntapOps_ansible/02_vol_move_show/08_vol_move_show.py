import os
import sys
import json
from collections import defaultdict
from datetime import datetime

# Get the directory containing the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project_directory)
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path
sys.path.append(parent_dir)

class VolumeMoveStatus:
    def __init__(self, vol_move_file, vol_size_file):
        self.vol_move_file = vol_move_file
        self.vol_size_file = vol_size_file
        self.data = self.load_json_data(vol_move_file)
        self.size_data = self.load_json_data(vol_size_file)
        self.records = []

    def load_json_data(self, json_file):
        with open(json_file, 'r') as file:
            return json.load(file)

    def process_records(self):
        size_dict = {record['volume']: record['size'] for record in self.size_data['msg']['records']}

        for record in self.data['msg']['records']:
            source_aggregate = record['source_aggregate']
            destination_aggregate = record['destination_aggregate']
            percent_complete = record['percent_complete']
            volume = record['volume']
            phase = record['phase']
            state = record['state']
            size = size_dict.get(volume, 'N/A')  # Get the size from the size data or 'N/A' if not found

            self.records.append({
                'source_aggregate': source_aggregate,
                'destination_aggregate': destination_aggregate,
                'percent_complete': percent_complete,
                'volume': volume,
                'size': size,
                'phase': phase,
                'state': state
            })

    def generate_table(self):
        header = ["Source Aggregate", "Destination Aggregate", "Volume", "Size (TB)", "Percent Complete", "State"]
        table = []

        for record in self.records:
            source_aggregate = record['source_aggregate']
            destination_aggregate = record['destination_aggregate']
            percent_complete = record['percent_complete']
            volume = record['volume']
            size_tb = round(record['size'] / (1024 ** 4), 2) if record['size'] != 'N/A' else 'N/A'  # Convert bytes to TB
            state = record['state']
            table.append([source_aggregate, destination_aggregate, volume, size_tb, percent_complete, state])

        return header, table

    def display_status(self):
        current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M")
        header, table = self.generate_table()

        print()
        print()
        print(f"Volume Move Status On {current_datetime}")
        print("#" * 40)
        print("-" * 140)
        print(f"{header[0]:<30}|{header[1]:<30}|{header[2]:<30}|{header[3]:<15}|{header[4]:<16}|{header[5]:<15}|")
        print("-" * 140)

        for row in table:
            print(f"{row[0]:<30}|{row[1]:<30}|{row[2]:<30}|{row[3]:<15}|{row[4]:<16}|{row[5]:<15}|")

        print("-" * 140)
        print()
        print()


class AggregateUsage:
    def __init__(self, json_file):
        self.json_file = json_file
        self.data = self.load_json_data()

    def load_json_data(self):
        with open(self.json_file, 'r') as file:
            return json.load(file)

    def generate_table(self):
        header = ["Aggregate", "Volumes on Disk", "Used on Disk in TB", "Size in TB", "Used Percent"]
        table = []

        for record in self.data['msg']['records']:
            aggregate = record['aggregate']
            volcount = record['volcount']
            usedsize_tb = record['usedsize'] / (1024 ** 4)  # Convert bytes to TB
            size_tb = record['size'] / (1024 ** 4)  # Convert bytes to TB
            percent_used = record['percent_used']
            table.append([aggregate, volcount, round(usedsize_tb, 2), round(size_tb, 2), percent_used])

        return header, table

    def display_usage(self):
        header, table = self.generate_table()

        print("-" * 97)
        print(f"{header[0]:<24}|{header[1]:<17}|{header[2]:<19}|{header[3]:<19}|{header[4]:<13}|")
        print("-" * 97)

        for row in table:
            print(f"{row[0]:<24}|{row[1]:<17}|{row[2]:<19}|{row[3]:<19}|{row[4]:<13}|")

        print("-" * 97)
        print("New info in about 3 hours, or if there’s nothing left to do :-)")
        print()

def main():
    server_ips = ['195.227.206.44', '195.227.213.185']
    for ip in server_ips:
       print("-" * 80)
       print(ip)
       vol_move_file1 = f'json/volmove_display_vol_move_{ip}.json'
       vol_size_file_path1 = f'json/volmove_display_moving_vol_size_{ip}.json'
       aggr_usage_file1 = f'json/volmove_display_aggr_{ip}.json'
       #print(aggr_usage_file1)
       vol_move_file = os.path.abspath(vol_move_file1)
       vol_size_file_path = os.path.abspath(vol_size_file_path1)
       aggr_usage_file = os.path.abspath(aggr_usage_file1)
       #print(aggr_usage_file)
       volume_move_status1 = VolumeMoveStatus(vol_move_file, vol_size_file_path)
       volume_move_status1.process_records()
       volume_move_status1.display_status()

       aggregate_usage1 = AggregateUsage(aggr_usage_file)
       aggregate_usage1.display_usage()


if __name__ == "__main__":
    main()



