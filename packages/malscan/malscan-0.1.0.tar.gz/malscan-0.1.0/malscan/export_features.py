import csv
import hashlib
import os


def generate_md5(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
        md5_hash = hashlib.md5(data).hexdigest()
    return md5_hash


class FeatureExporter:
    def __init__(self, analyser):
        self.analyser = analyser

    def export_features(self, method_name, file_path):
        # Call the method from the analyser instance
        features = getattr(self.analyser, method_name)()

        # Generate the MD5 hash for the file
        md5_label = generate_md5(self.analyser.file_path)

        # Prepare the data for CSV
        headers = ['MD5_Label'] + list(features.keys())
        data = [md5_label] + list(features.values())

        # Check if the file already exists
        file_exists = os.path.isfile(file_path)

        # Open the file in append mode ('a') and write the features to it
        with open(file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            # If the file didn't exist before, write the headers
            if not file_exists:
                writer.writerow(headers)
            # Write the data
            writer.writerow(data)
