from setuptools import setup, find_packages
from pathlib import Path
import platform

# Determine the correct requirements file
# requirements_file = "requirements_macos.txt" if platform.system() == "Darwin" else "requirements.txt"
requirements_file = "requirements.txt"

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


# Function to read the requirements from the file
def read_requirements(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

setup(
    name='audiotimer',
    version='0.4.0',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'audiotimer=audiotimer.__main__:main'
        ]
    },
    install_requires=read_requirements(requirements_file),
    package_data={
        # If 'audiotimer' is your package directory and 'config.ini' is directly inside it
        'audiotimer': ['config.ini'],
    },
    include_package_data=True,  # This tells setuptools to include files defined in MANIFEST.in or package_data
)

