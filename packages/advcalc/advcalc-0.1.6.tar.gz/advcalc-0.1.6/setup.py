from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

VERSION = '0.1.6' 
DESCRIPTION = 'Advanced Python Calculator With an API'

setup(
    name="advcalc", 
    version=VERSION,
    author="Zack",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),  # Make sure this correctly locates all your packages
    keywords=['python', 'calculator'],
    license="MIT",  # Verify that this license matches your project
    entry_points={
        "console_scripts": [
            "advcalc=advcalc.cli:cli",
        ],
    },
    install_requires=["setuptools>=61.0"]
)
