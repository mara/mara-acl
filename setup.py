from setuptools import setup, find_packages

setup(
    name='mara-acl',
    version='1.5.1',

    description='Default ACL implementation for Mara',

    python_requires='>=3.6',

    install_requires=[
        'mara-db >= 1.3.0',
        'mara-page >= 1.4.0'
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={},
)

