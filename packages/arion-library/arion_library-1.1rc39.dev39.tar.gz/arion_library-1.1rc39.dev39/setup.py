
from setuptools import setup, find_packages
import os

# Get the absolute path of the directory containing setup.py
base_dir = os.path.abspath(os.path.dirname(__file__))
required_txt_path = os.path.join(base_dir, "required.txt")
if os.path.exists(required_txt_path):
    with open(required_txt_path) as f:
        required = f.read().splitlines()
else:
    required = []

setup(
    name='arion_library',  # Replace with your package name
    version='1.1rc39.dev39',  # Replace with your package version
    author='Heni Nechi',  # Replace with your name
    author_email='h.nechi@arion-tech.com',  # Replace with your email
    url='https://github.com/Ariontech/ArionLibrary.git',  # Replace with your repository URL
    packages=find_packages(),  # Automatically find all packages
    python_requires='>=3.8',  # Specify Python version requirements
    install_requires=required,
)
        # 'pyodbc',
        # 'pytest',
        # 'azure-core'
        # 'azure-data-tables'
        # 'azure-storage-blob'
        # 'python-dotenv'
        # 'pytest'
