import os
import csv
import xml.etree.ElementTree as ET

folder_path = 'C:/Users/kanha930/Documents/Desktop/New folder'
output_file = 'output.csv'

# Define the fields to extract and their desired order
fields = ['Host_alias', 'local', 'enabled', 'Origin', 'transport', 'Address', 'Port', 'user', 'readonly', 'Ftprootpath', 'Inbox', 'Outbox', 'Recieved', 'Sentbox']
field_order = fields + ['Aliases', 'Commands']

# Create a list to store the extracted data
data = []

# Iterate through the XML files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.xml'):
        file_path = os.path.join(folder_path, filename)

        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract the desired fields from the XML file
        extracted_fields = {field: '' for field in fields}
        extracted_fields['Host_alias'] = root.get('alias')
        extracted_fields['local'] = root.get('local')
        extracted_fields['enabled'] = root.get('enabled')

        for child in root:
            if child.tag in fields:
                extracted_fields[child.tag] = child.text.strip()

        # Extract the aliases and commands under each "Action" tag
        actions = root.findall('.//Action')
        aliases = []
        commands = []
        for action in actions:
            alias = action.get('alias')
            if alias is not None:
                aliases.append(alias)
            commands_elem = action.find('Commands')
            if commands_elem is not None:
                commands.append(commands_elem.text.strip())

        extracted_fields['Aliases'] = '\n'.join(aliases)
        extracted_fields['Commands'] = '\n'.join(commands)

        data.append(extracted_fields)

# Write the extracted data to the CSV file with the desired field order
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_order)
    writer.writeheader()
    writer.writerows(data)
