# setup.py

from setuptools import setup, find_packages

packs= find_packages()
print(packs)

setup(
    name='heimdall_tools',
    version='0.0.1',
    packages=find_packages(),
    #packages=['heimdall_tools'],
    install_requires=[
        'boto3',
        # Add any other dependencies here
    ],
)
