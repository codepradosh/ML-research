import os
import csv
import xml.etree.ElementTree as ET

folder_path = '/home/m809083/hosts'
output_file = 'output.csv'

# Create the CSV file and write the header
fields = ['Host_alias', 'local', 'enabled', 'Origin', 'transport', 'Address', 'Port', 'user', 'readonly', 'Ftprootpath', 'Inbox', 'Outbox', 'Recieved', 'Sentbox', 'Alias', 'Command']
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fields)

    # Iterate through the XML files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            file_path = os.path.join(folder_path, filename)

            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Check if the file contains "Inbound" or "Outbound" in the filename
            if 'Inbound' in filename or 'Outbound' in filename:
                commands = root.findall('.//Action[@actiontype="Commands"]')

                # Extract the desired fields and commands
                for command in commands:
                    alias = command.get('alias')
                    command_text = command.find('Commands').text
                    
                    extracted_fields = []
                    for field in fields[:13]:
                        element = root.find(field)
                        if element is not None:
                            extracted_fields.append(element.text)
                        else:
                            extracted_fields.append('')
                    
                    extracted_fields.extend([alias, command_text])
                    writer.writerow(extracted_fields)
