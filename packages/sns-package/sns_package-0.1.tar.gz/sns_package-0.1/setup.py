# setup.py

from setuptools import setup, find_packages

setup(
    name='sns_package',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'json',
        'boto3',
        # Add any other dependencies here
    ],
)
