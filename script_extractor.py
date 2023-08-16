import os
import csv
import xml.etree.ElementTree as ET

# Folder paths and output file
folder_path = 'C:/Users/ppriyad2/PycharmProjects/python Project5/hosts'
output_file = 'output.csv'

# Define the fields to extract and their desired order
fields = ['Host_alias', 'Alias', 'Command']
# Or if you want to use the fields from code 2:
# fields = ['Host_alias', 'local', 'enabled', 'Origin', 'transport', 'Address', 'Port', 'user', 'readonly', 'Ftprootpath', 'Inbox', 'Outbox', 'Recieved', 'Sentbox']

# Create a list to store the extracted data
data = []

# Iterate through the XML files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.xml'):
        file_path = os.path.join(folder_path, filename)
        
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Check if the file name contains 'Inbound' or 'Outbound'
        if 'Inbound' in filename or 'Outbound' in filename:
            # Find Action Type = "Commands" and extract Alias and Command fields
            commands = root.findall('.//Action[@actiontype="Commands"]')
            for command in commands:
                extracted_fields = {field: "" for field in fields}
                extracted_fields['Host_alias'] = root.get('alias')
                extracted_fields['Alias'] = command.get('alias')
                extracted_fields['Command'] = command.find('Commands').text
                data.append(extracted_fields)

# Write the extracted data to the CSV file with the desired field order
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)
