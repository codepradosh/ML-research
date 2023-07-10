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

            # Group the Aliases and Commands under each Action Type
            action_types = root.findall('.//Action')
            for i, action_type in enumerate(action_types):
                aliases = []
                commands = []
                actions = action_type.findall('Action')
                for action in actions:
                    alias = action.get('alias')
                    commands_elem = action.find('Commands')
                    if alias is not None:
                        aliases.append(alias)
                    if commands_elem is not None:
                        commands.append(commands_elem.text.strip())

                extracted_fields[f'Action_Type_{i+1}'] = action_type.get('actiontype')
                extracted_fields[f'Aliases_{i+1}'] = '\n'.join(aliases)
                extracted_fields[f'Commands_{i+1}'] = '\n'.join(commands)

            # Write the extracted fields to the CSV file
            if csvfile.tell() == 0:  # Write header only once
                writer.writerow(extracted_fields.keys())
            writer.writerow(extracted_fields.values())
