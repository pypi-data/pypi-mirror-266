# Malscan

Malscan is a Python-based malware analysis tool. It uses various libraries such as 'setuptools', 'r2pipe', 'pefile', 'filetype', and 'frida' to perform its operations. The package includes modules for static, dynamic analysis and exporting features.

## Features

- Static Analysis: Extracts file headers, metadata, and strings from a malware file. It also calculates the Shannon entropy for each string and counts the frequency of specific string patterns.
- Feature Export: Exports the results of a specified analysis method to a CSV file.
- Dynamic Analysis: Uses Frida to perform dynamic analysis on a malware file. It can hook functions, monitor system calls, and extract information about the malware's behavior.

## Installation

To install Malscan, you need Python 3.10 or higher. You can install the package using pip:

```bash
pip install malscan
```

## Requirements

- Python 3.10 or higher
- Radare2
- setuptools
- r2pipe
- pefile
- filetype
- frida

## Example Usage

```python
from malscan.static_analysis import StaticAnalyser
from malscan.export_features import FeatureExporter
import os

# Specify the directory to analyze
directory_path = r"Extras/analysis_files"

# Iterate over all the files in the directory
for file_name in os.listdir(directory_path):
    # Construct the full file path
    file_path = os.path.join(directory_path, file_name)

    # Skip if the current file is a directory
    if os.path.isdir(file_path):
        continue

    # Instantiate StaticAnalyser with a file path
    analyser = StaticAnalyser(file_path=file_path)

    # Perform static analysis
    analysis_results = analyser.extract_file_headers()

    # Output analysis results
    print(f"Static Analysis Results for {file_name}:")
    for category, result in analysis_results.items():
        print(f"{category}: {result}")

    # Export features to CSV
    exporter = FeatureExporter(analyser)
    exporter.export_features(method_name="extract_file_headers", file_path="features.csv")
```
```text
    This is an example of how a user will utilise the framework to analyse file headers in their malware directory, analysing a series of files and exporting the results to a csv file
```

## License
This project is licensed under the MIT License - see the LICENSE.md file for details. 
