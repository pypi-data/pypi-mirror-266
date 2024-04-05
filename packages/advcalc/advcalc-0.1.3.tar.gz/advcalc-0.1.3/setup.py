from setuptools import setup, find_packages

with open("README.md", "r") as fh:
        LONG_DESCRIPTION = fh.read()

VERSION = '0.1.3' 
DESCRIPTION = 'Advanced Python Calculator'

setup(
        name="advcalc", 
        version=VERSION,
        author="Zack",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        packages=find_packages(),
        keywords=['python', 'calculator'],
        license="MIT"
)