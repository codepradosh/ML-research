import rocksdb
import csv

# Path to the .db file
db_path = '/cs/anomaly/scripts/prediction/TSAnomaly_Weak_Forward_Pred-data/v1/tables/forward_weak_pred_table-1.db'

# Open the RocksDB database
db = rocksdb.DB(db_path, rocksdb.Options(create_if_missing=False), read_only=True)

# Output CSV file path
output_csv_file = 'output.csv'

# Create a CSV file and write the data
with open(output_csv_file, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)

    # Write the CSV header
    csv_writer.writerow(['Key', 'Value'])

    # Iterate over all key-value pairs in the database
    for key, value in db.iterator():
        key_str = key.decode('utf-8')
        value_str = value.decode('utf-8')
        csv_writer.writerow([key_str, value_str])

print(f"Data from the RocksDB database has been written to {output_csv_file}.")
