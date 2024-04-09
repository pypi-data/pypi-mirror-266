from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0.3'
DESCRIPTION = "A Python package for cleaning up cluttered files and organizing them into respective folders."
# Setting up
setup(
    name="pi-folder-organizer",
    version=VERSION,
    author="Qadeer Ahmad",
    author_email="mrqdeer1231122@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    
    keywords=['python', 'file organization', 'file cleanup', 'cluttered files', 
              'folder management', 'data organization', 'file management', 
              'data cleanup', 'Python package', 'developer tools', 'data processing',
              'file sorting', 'data structuring', 'automated file organization', 
              'Python library', 'data management', 'data handling', 'file optimization', 'data optimization'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    
)
