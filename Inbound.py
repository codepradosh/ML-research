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

            # Initialize a dictionary for the extracted fields
            extracted_fields = {field: '' for field in fields}

            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract the desired fields from the XML file
            extracted_fields['Host_alias'] = root.get('alias')
            extracted_fields['local'] = root.get('local')
            extracted_fields['enabled'] = root.get('enabled')

            # Check if the file name contains 'Inbound' or 'Outbound'
            if 'Inbound' in filename or 'Outbound' in filename:
                # Find Action Type = "Commands" and extract Alias and Command fields
                commands = root.findall('.//Action[@actiontype="Commands"]')
                if commands:
                    extracted_fields['Alias'] = ' '.join(command.get('alias') for command in commands)
                    extracted_fields['Command'] = ' '.join(command.find('Commands').text for command in commands)

            # Write the extracted fields to the CSV file
            writer.writerow(extracted_fields)
