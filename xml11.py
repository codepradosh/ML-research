import os
import csv
import xml.etree.ElementTree as ET

folder_path = 'C:/Users/kanha930/Documents/Desktop/New folder'
output_file = 'output.csv'
fields = ['Host_alias', 'local', 'enabled', 'Origin', 'transport', 'Address', 'Port', 'user', 'readonly', 'Ftprootpath', 'Inbox', 'Outbox', 'Recieved', 'Sentbox', 'Alias', 'Commands']

# Create the CSV file and write the header
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

    # Iterate through the XML files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            file_path = os.path.join(folder_path, filename)

            # Initialize a dictionary for the extracted fields
            extracted_fields = {field: '' for field in fields}

            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract the desired fields from the XML file
            extracted_fields['Host_alias'] = root.get('alias')
            extracted_fields['local'] = root.get('local')
            extracted_fields['enabled'] = root.get('enabled')

            for field in fields[3:]:
                element = root.find(field)
                if element is not None:
                    extracted_fields[field] = element.text

            # Extract the Alias and Commands from the Action tags
            actions = root.findall('.//Action')
            if actions:
                alias_list = []
                commands_list = []
                for action in actions:
                    alias = action.get('alias')
                    commands = action.find('Commands').text if action.find('Commands') is not None else ''
                    if alias:
                        alias_list.append(alias)
                    if commands:
                        commands_list.append(commands)
                extracted_fields['Alias'] = ', '.join(alias_list)
                extracted_fields['Commands'] = ', '.join(commands_list)

            # Encode the values as ASCII and ignore any characters that cannot be encoded
            encoded_fields = {k: v.encode('ascii', 'ignore').decode('ascii') for k, v in extracted_fields.items()}

            # Write the extracted fields to the CSV file
            writer.writerow(encoded_fields)
