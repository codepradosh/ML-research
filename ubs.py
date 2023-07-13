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

        # Find all action elements
        actions = root.findall('.//Action')

        for action in actions:
            # Extract the alias
            alias = action.get('alias')

            # Find the Commands element within the action
            commands_elem = action.find('Commands')

            if commands_elem is not None:
                # Extract the command text
                commands = commands_elem.text.strip()
            else:
                commands = ''

            # Create a dictionary to store the extracted fields
            extracted_fields = {
                'Host_alias': host_alias,
                'local': local,
                'enabled': enabled,
                'Alias': alias,
                'Commands': commands
            }

            data.append(extracted_fields)

# Extract all unique column names
column_names = set().union(*[d.keys() for d in data])

# Write the extracted data to the CSV file
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=column_names)
    writer.writeheader()
    writer.writerows(data)
