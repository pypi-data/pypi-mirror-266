from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('version.txt') as f:
    version = f.read()

setup(
    name='Stucent',
    version=version,
    packages=find_packages(),
    install_requires=requirements,
    # Add all other necessary package metadata
)
