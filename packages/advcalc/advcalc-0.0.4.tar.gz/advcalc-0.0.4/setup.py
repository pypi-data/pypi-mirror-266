from setuptools import setup, find_packages

VERSION = '0.0.4' 
DESCRIPTION = 'Advanced Python Calculator'
LONG_DESCRIPTION = 'An advanced Python calculator'

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
)