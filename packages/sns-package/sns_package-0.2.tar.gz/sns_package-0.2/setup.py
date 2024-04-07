# setup.py

from setuptools import setup, find_packages

setup(
    name='sns_package',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'boto3',
        # Add any other dependencies here
    ],
)
