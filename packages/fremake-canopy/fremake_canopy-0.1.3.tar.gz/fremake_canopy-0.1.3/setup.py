from setuptools import setup, find_packages

setup(
    name='fremake_canopy',
    version='0.1.3',
    description='Implementation of fremake',
    author='Thomas Robinson, Dana Singh, Bennett Chang',
    author_email='Thomas.Robinson@noaa.gov',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyyaml',
        'argparse',
        'jsonschema',
    ],
)
