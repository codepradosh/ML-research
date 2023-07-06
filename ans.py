import os
import csv
import xml.etree.ElementTree as ET

folder_path = '/home/m809083/hosts'
output_file = 'output.csv'


ignore_nested_tags = True

field_set = set()
for filename in os.listdir(folder_path):
    if filename.endswith('.xml'):
        file_path = os.path.join(folder_path, filename)
        tree = ET.parse(file_path)
        root = tree.getroot()
        for element in root.iter():
            if ignore_nested_tags and any(child.tag == element.tag for child in element.iter()):
                continue
            field_set.add(element.tag)

fields = sorted(list(field_set))

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            file_path = os.path.join(folder_path, filename)
            extracted_fields = {field: '' for field in fields}
            tree = ET.parse(file_path)
            root = tree.getroot()
            for element in root.iter():
                if ignore_nested_tags and any(child.tag == element.tag for child in element.iter()):
                    continue
                extracted_fields[element.tag] = element.text
            writer.writerow(extracted_fields)
