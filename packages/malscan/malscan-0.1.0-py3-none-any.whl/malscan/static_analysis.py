# libraries needed
import r2pipe
import hashlib
import os
import pefile
import filetype
import collections
import math
import re


def calculate_entropy(s):
    """
    Calculate the Shannon entropy of a string

    Parameters
    ----------
    s : str
        The string for which to calculate the entropy

    Returns
    -------
    float
        The Shannon entropy of the string
    """

    # shannon entropy calculation HSh = −Σipilog pi
    p, lns = collections.Counter(s), float(len(s))
    return -sum(count / lns * math.log(count / lns, 2) for count in p.values())


def count_string_patterns(strings):
    """
    Count the frequency of specific string patterns in a list of strings

    Parameters
    ----------
    strings : list
        The list of strings to search

    Returns
    -------
    dict
        A dictionary where the keys are the string patterns and the values are the counts
    """
    patterns = ['http://', 'https://', 'HKEY_']
    pattern_frequencies = {pattern: 0 for pattern in patterns}

    for s in strings:
        for pattern in patterns:
            if re.search(pattern, s['string']):
                pattern_frequencies[pattern] += 1

    return pattern_frequencies


class StaticAnalyser:
    """
    A class to perform static analysis on a malware file.

    ...

    Attributes
    ----------
    file_path : str
        the path to the malware file
    r2 : r2pipe.open
        an r2pipe object for interacting with the radare2 disassembler

    Methods
    -------
    full_analysis()
        Perform static analysis on the malware file.
    extract_hashes()
        Extract MD5, SHA1 and SHA256 hashes from the malware file.
    compare_hashes(known_malware_hashes)
        Compare extracted hashes against a list of known malware hashes.
    analyse_opcodes()
        Analyze opcodes within the binary file using r2pipe.
    extract_metadata()
        Extract metadata from the malware file.
    extract_file_headers()
        Extract file headers from the malware file.
    analyse_strings()
        Analyse strings within the binary file using r2pipe.
    """

    def __init__(self, file_path):
        """
        Constructs all the necessary attributes for the StaticAnalyzer object.
        parameters
        ----------
            file_path: str
                the path to the malware file
        """
        self.file_path = file_path
        self.r2 = r2pipe.open(file_path)  # Opens radare2 session for the file

    def full_analysis(self):
        """
        Perform static analysis on the malware file.

        returns
        -------
            dict
                a dictionary containing the results of the static analysis
        """

        try:
            metadata = self.extract_metadata()
            file_headers = self.extract_file_headers()
            strings_analysis = self.analyse_strings()
            hashes = self.extract_hashes()
            opcode = self.analyse_opcodes()

            return {
                'metadata': metadata,
                'file_headers': file_headers,
                'strings_analysis': strings_analysis,
                'hashes': hashes,
                'opcode': opcode,
            }
        except FileNotFoundError:
            print(f"File {self.file_path} not found.")
            return {"error": "File not found"}
        except Exception as e:
            print(f"An error occurred while analyzing {self.file_path}: {str(e)}")
            return {"error": str(e)}

    def extract_hashes(self):
        """
        Extract MD5, SHA1 and SHA256 hashes from the malware file.

        Returns
        -------
        dict
            a dictionary containing the MD5, SHA1 and SHA256 hashes of the malware file
        """
        try:
            with open(self.file_path, 'rb') as file:
                data = file.read()

            md5_hash = hashlib.md5(data).hexdigest()
            sha1_hash = hashlib.sha1(data).hexdigest()
            sha256_hash = hashlib.sha256(data).hexdigest()

            return {
                'md5': md5_hash,
                'sha1': sha1_hash,
                'sha256': sha256_hash
            }

        except Exception as e:
            print(f"An error occurred while extracting hashes: {str(e)}")
            return {"error": str(e)}

    def analyse_opcodes(self):
        """
        Analyze opcodes within the binary file using r2pipe.

        Returns
        -------
        dict
            a dictionary containing the frequencies of each opcode in the binary file
        """
        try:
            # Perform automatic analysis
            self.r2.cmd('aaa')
            # Disassemble the binary file and extract the opcodes
            disassembly = self.r2.cmdj('pdj 1000')

            # Initialize a dictionary to store the opcode frequencies
            opcode_frequencies = {}
            for instruction in disassembly:
                # Some lines in the disassembly might not contain an opcode
                if 'opcode' in instruction:
                    # Extract the opcode from the instruction
                    opcode = instruction['opcode'].split()[0]
                    # Update the opcode frequencies
                    if opcode in opcode_frequencies:
                        opcode_frequencies[opcode] += 1
                    else:
                        opcode_frequencies[opcode] = 1

            # If the dictionary is empty, print a message
            if not opcode_frequencies:
                print("No opcodes found in the binary file.")

            return opcode_frequencies

        except Exception as e:
            print(f"An error occurred while analyzing opcodes: {str(e)}")
            return {"error": str(e)}

    def extract_metadata(self):
        """
        Extract metadata from the malware file.

        Returns
        -------
        dict
            a dictionary containing the metadata of the malware file
        """
        try:
            file_info = os.stat(self.file_path)  # File information
            file_size = file_info.st_size  # File size in bytes
            last_modified = file_info.st_mtime  # Last modified time

            # Determine file type
            kind = filetype.guess(self.file_path)
            if kind is None:
                file_type = 'Unknown'
            else:
                file_type = kind.mime

            return {
                'file_size': file_size,
                'last_modified': last_modified,
                'file_type': file_type
            }

        except Exception as e:
            print(f"An error occurred while extracting metadata: {str(e)}")
            return {"error": str(e)}

    def extract_file_headers(self):
        """
        Extract file headers from the malware file.

        Returns
        -------
        dict
            a dictionary containing the file headers of the malware file
        """
        try:
            pe = pefile.PE(self.file_path)

            imported_functions = []
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                for func in entry.imports:  # Iterate over the imported functions
                    if func.name is not None:  # Check if the function name is not None
                        imported_functions.append(func.name.decode('utf-8'))

            exported_functions = []
            if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):  # Check if the PE file has exported functions
                for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:  # Iterate over the exported functions
                    if exp.name is not None:  # Check if the function name is not None
                        exported_functions.append(exp.name.decode('utf-8'))

            if len(exported_functions) == 0:
                exported_functions = 0

            headers = {
                'Machine': hex(pe.FILE_HEADER.Machine),
                'TimeDateStamp': hex(pe.FILE_HEADER.TimeDateStamp),
                'NumberOfSections': hex(pe.FILE_HEADER.NumberOfSections),
                'PointerToSymbolTable': hex(pe.FILE_HEADER.PointerToSymbolTable),
                'NumberOfSymbols': hex(pe.FILE_HEADER.NumberOfSymbols),
                'SizeOfOptionalHeader': hex(pe.FILE_HEADER.SizeOfOptionalHeader),
                'Characteristics': hex(pe.FILE_HEADER.Characteristics),
                'ImportedFunctions': imported_functions,
                'ExportedFunctions': exported_functions
            }

            return headers

        except Exception as e:
            print(f"An error occurred while extracting file headers: {str(e)}")
            return {"error": str(e)}

    def analyse_strings(self):
        """
            This method extracts all strings from the binary file using radare2,
            It then calculates the Shannon entropy for each string
            It also calculates the distribution of string lengths
            It counts the frequency of specific string patterns such as 'https://', 'https://', and 'HKEY_', etc.

        Returns
        -------

        dict
                A dictionary containing the results of the string analysis. The dictionary has the following keys:
            - 'string_entropies':
            - 'string_length_distribution':
            - 'pattern_frequencies':
        """
        try:
            # Use r2pipe to extract all strings from the binary file
            self.r2.cmd('aaa')
            strings = self.r2.cmdj('izj')  # Extract strings in json format

            # Calculate string entropy
            string_entropies = [calculate_entropy(s['string']) for s in strings]

            # Calculate string length distribution
            string_lengths = [len(s['string']) for s in strings]
            string_length_distribution = collections.Counter(string_lengths)

            # Count frequency of specific string patterns
            pattern_frequencies = count_string_patterns(strings)

            return {
                'string_entropies': string_entropies,
                'string_length_distribution': dict(string_length_distribution),
                'pattern_frequencies': pattern_frequencies
            }

        except Exception as e:
            print(f"An error occurred while analyzing strings: {str(e)}")
            return {"error": str(e)}
