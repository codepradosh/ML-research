import os
import csv
import xml.etree.ElementTree as ET

folder_path = 'C:/Users/kanha930/Documents/Desktop/New folder'
output_file = 'output.csv'

# Create a list to store the extracted data
data = []

# Iterate through the XML files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.xml'):
        file_path = os.path.join(folder_path, filename)

        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract the host alias, local, and enabled fields
        host_alias = root.get('alias')
        local = root.get('local')
        enabled = root.get('enabled')

        # Find all action elements with actiontype="Commands"
        actions = root.findall('.//Action[@actiontype="Commands"]')

        for action in actions:
            # Extract the alias and commands
            alias = action.get('alias')
            commands = action.findall('.//Command')

            # Iterate over multiple commands and extract their text
            command_texts = [command.text.strip() for command in commands]

            # Create a dictionary to store the extracted fields
            extracted_fields = {
                'Host_alias': host_alias,
                'local': local,
                'enabled': enabled,
                'Alias': alias
            }

            # Add each command to the dictionary with a dynamic column name
            for i, command_text in enumerate(command_texts):
                extracted_fields[f'Command_{i+1}'] = command_text

            data.append(extracted_fields)

# Extract all unique column names
column_names = set().union(*[d.keys() for d in data])

# Write the extracted data to the CSV file
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=column_names)
    writer.writeheader()
    writer.writerows(data)
