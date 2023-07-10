import os
import csv
import xml.etree.ElementTree as ET

folder_path = 'C:/Users/kanha930/Documents/Desktop/New folder'
output_file = 'output.csv'
fields = ['Host_alias', 'local', 'enabled', 'Origin', 'transport', 'Address', 'Port', 'user', 'readonly', 'Ftprootpath', 'Inbox', 'Outbox', 'Recieved', 'Sentbox']

# Create the CSV file and write the header
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)

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
            for field in fields[3:]:
                element = root.find(field)
                if element is not None:
                    extracted_fields[field] = element.text

            # Extract the Alias and Commands from the Action tags
            actions = root.findall('.//Action')
            if actions:
                for i, action in enumerate(actions):
                    alias = action.get('alias')
                    commands = action.find('Commands').text if action.find('Commands') is not None else ''
                    extracted_fields[f'Alias_{i+1}'] = alias
                    extracted_fields[f'Commands_{i+1}'] = commands

            # Write the extracted fields to the CSV file
            if csvfile.tell() == 0:  # Write header only once
                writer.writerow(extracted_fields.keys())
            writer.writerow(extracted_fields.values())
