from setuptools import setup, find_packages

with open("README.md", "r") as fh:
        LONG_DESCRIPTION = fh.read()

VERSION = '0.1.4' 
DESCRIPTION = 'Advanced Python Calculator With an API'

setup(
        name="advcalc", 
        build_backend="setuptools.build_meta",
        version=VERSION,
        author="Zack",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        packages=find_packages(),
        keywords=['python', 'calculator'],
        license="MIT",
        entry_points={
                "console_scripts": [
                        "advcalc=advcalc.cli:cli",
                ],
        },
        install_requires = ["setuptools>=61.0"]
)