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

        # Extract the desired fields from the XML file
        extracted_fields = {field: '' for field in fields}
        extracted_fields['Host_alias'] = root.get('alias')
        extracted_fields['local'] = root.get('local')
        extracted_fields['enabled'] = root.get('enabled')
        extracted_fields['Origin'] = root.get('Origin', '')
        extracted_fields['transport'] = root.get('transport', '')
        extracted_fields['Address'] = root.find('Address').text.strip()
        extracted_fields['Port'] = root.find('Port').text.strip()
        extracted_fields['user'] = root.find('Username').text.strip()
        extracted_fields['readonly'] = root.find('Readonly').text.strip()
        extracted_fields['Ftprootpath'] = root.find('Ftprootpath').text.strip()
        extracted_fields['Inbox'] = root.find('Inbox').text.strip()
        extracted_fields['Outbox'] = root.find('Outbox').text.strip()
        extracted_fields['Recieved'] = root.find('Receivedbox').text.strip()
        extracted_fields['Sentbox'] = root.find('Sentbox').text.strip()

        # Extract the aliases and commands under each "Action" tag
        actions = root.findall('.//Action')
        for i, action in enumerate(actions):
            aliases = []
            commands_elem = action.find('Commands')
            if commands_elem is not None:
                commands = commands_elem.text.strip()
            else:
                commands = ''
            alias = action.get('alias')
            if alias is not None:
                aliases.append(alias)

            extracted_fields[f'Action_Type_{i+1}'] = action.get('actiontype')
            extracted_fields[f'Aliases_{i+1}'] = '\n'.join(aliases)
            extracted_fields[f'Commands_{i+1}'] = commands

        data.append(extracted_fields)

# Extract all unique column names
column_names = set().union(*[d.keys() for d in data])

# Write the extracted data to the CSV file
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=column_names)
    writer.writeheader()
    writer.writerows(data)
