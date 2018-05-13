from setuptools import setup, find_packages

setup(
    name='mara-acl',
    version='1.4.0',

    description='Default ACL implementation for Mara',

    install_requires=[
        'mara-db>=3.0.0',
        'mara-page>=1.2.3',
        'mara-config>=0.1',
    ],

    dependency_links=[
        'git+https://github.com/mara/mara-page.git@1.2.3#egg=mara-page-1.2.3',
        'git+https://github.com/mara/mara-db.git@3.0.0#egg=mara-db-3.0.0',
        'git+https://github.com/mara/mara-config.git@0.1#egg=mara-config-0.1',
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={},
)

