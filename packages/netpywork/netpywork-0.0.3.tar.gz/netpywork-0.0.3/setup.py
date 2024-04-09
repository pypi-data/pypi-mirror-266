from setuptools import setup, find_packages
from pathlib import Path
from netpywork.constants import VERSION
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
name='netpywork',
version=VERSION,
author='Murky',
author_email='shooterkingof@gmail.com',
description='Python library that simplifies UDP and TCP server and client',
packages=find_packages(),
classifiers=[
'Programming Language :: Python :: 3',
'License :: OSI Approved :: MIT License',
'Operating System :: OS Independent',
],
long_description=long_description,
long_description_content_type='text/markdown',
python_requires='>=3.8',
url="https://github.com/MurkyYT/netpywork",
)