from setuptools import setup, find_packages

with open("README.md", "r") as fh:
        LONG_DESCRIPTION = fh.read()

VERSION = '0.0.6' 
DESCRIPTION = 'Advanced Python Calculator'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="advcalc", 
        version=VERSION,
        author="Zack",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        keywords=['python', 'calculator'],
        license="MIT"
)