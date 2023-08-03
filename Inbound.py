import os
import csv
import xml.etree.ElementTree as ET

folder_path = '/home/m809083/hosts'
output_file = 'output.csv'
fields = ['Host_alias', 'local', 'enabled', 'Origin', 'transport', 'Address', 'Port', 'user', 'readonly', 'Ftprootpath', 'Inbox', 'Outbox', 'Recieved', 'Sentbox', 'Alias', 'Command']

# Create the CSV file and write the header
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

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
                    extracted_fields = {field: '' for field in fields}
                    extracted_fields['Host_alias'] = root.get('alias')
                    extracted_fields['local'] = root.get('local')
                    extracted_fields['enabled'] = root.get('enabled')
                    extracted_fields['Alias'] = command.get('alias')
                    extracted_fields['Command'] = command.find('Commands').text

                    # Write the extracted fields to the CSV file
                    writer.writerow(extracted_fields)
