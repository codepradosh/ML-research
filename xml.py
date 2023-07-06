import os
import csv
import xml.etree.ElementTree as ET

folder_path = '/home/m821059/hosts'
output_file = 'output.csv'
fields = ['Host_alias', 'LOCAL', 'Origin', 'enabled', 'transport', 'Address', 'Port', 'user', 'readonly', 'Ftprootpath', 'Inbox', 'Outbox', 'Recieved', 'Sentbox']

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
            for field in fields:
                element = root.find(field)
                if element is not None:
                    extracted_fields[field] = element.text

            # Write the extracted fields to the CSV file
            writer.writerow(extracted_fields)
