from setuptools import find_packages, setup

setup(
    name='malscan',
    packages=find_packages(include=['malscan']),
    version='0.1.0',
    install_requires=[
        'setuptools~=69.1.1',
        'r2pipe~=1.8.8',
        'pefile~=2023.2.7',
        'filetype~=1.2.0',
        'frida~=16.2.1'],
    python_requires='>=3.10',
    description='A Python package for automated static and dynamic analysis of malware samples. Supports both static '
                'and dynamic analysis techniques with feature extraction and export capabilities for static features.',
    author='Raheem Qamar',
)
