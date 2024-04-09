from setuptools import setup, find_packages

setup(
    name='beacon2-import',
    version='1.0.1',
    author='Khaled Jumah',
    author_email='khalled.jooma@yahoo.com',
    description='Seamlessly import and query genomic variant data from a beacon',
    license = 'CC-BY-NC-4.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'beacon2-import = import.beacon2_import:beacon2_import',
            'beacon2-search = search.beacon2_search:beacon_query'
        ]
    },
    install_requires=[
       'jsonschema',
       'argparse',
       'asyncio',
       'datetime',
       'dataclasses',
       'typing',
       'bioblend',
       'cyvcf2',
       'pymongo',
       'conf'
    ],
    dependency_links=[
        'git+https://github.com/CSCfi/beacon-python#egg=beacon-python',
    ]
)
