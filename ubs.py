import os
import csv
import xml.etree.ElementTree as ET

folder_path = 'C:/Users/kanha930/Documents/Desktop/New folder'
output_file = 'output.csv'

# Define the fields to extract
fields = ['Host_alias', 'local', 'enabled', 'Origin', 'transport', 'Address', 'Port', 'user', 'readonly', 'Ftprootpath', 'Inbox', 'Outbox', 'Recieved', 'Sentbox']

# Create a list to store the extracted data
data = []

# Iterate through the XML files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.xml'):
        file_path = os.path.join(folder_path, filename)

        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract the aliases and commands from the XML file
        actions = root.findall('.//Action[@actiontype="Commands"]')
        for action in actions:
            alias = action.get('alias')
            commands_elem = action.find('Commands')
            commands = commands_elem.text.strip() if commands_elem is not None else ''

            extracted_fields = {field: '' for field in fields}
            extracted_fields['Host_alias'] = root.get('alias')
            extracted_fields['local'] = root.get('local')
            extracted_fields['enabled'] = root.get('enabled')
            extracted_fields['Origin'] = root.get('Origin', '')
            extracted_fields['transport'] = root.get('transport', '')
            extracted_fields['Address'] = root.get('Address', '')
            extracted_fields['Port'] = root.get('Port', '')
            extracted_fields['user'] = root.get('user', '')
            extracted_fields['readonly'] = root.get('readonly', '')
            extracted_fields['Ftprootpath'] = root.get('Ftprootpath', '')
            extracted_fields['Inbox'] = root.get('Inbox', '')
            extracted_fields['Outbox'] = root.get('Outbox', '')
            extracted_fields['Recieved'] = root.get('Recieved', '')
            extracted_fields['Sentbox'] = root.get('Sentbox', '')
            extracted_fields['Alias'] = alias
            extracted_fields['Commands'] = commands

            data.append(extracted_fields)

# Extract all unique column names
column_names = set().union(*[d.keys() for d in data])

# Write the extracted data to the CSV file
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=column_names)
    writer.writeheader()
    writer.writerows(data)
