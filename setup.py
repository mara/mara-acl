from setuptools import setup, find_packages

setup(
    name='mara-acl',
    version='2.1.0',

    description='Default ACL implementation for Mara',

    python_requires='>=3.6',

    install_requires=[
        'mara-db >= 1.3.0',
        'mara-page >= 1.4.0'
    ],

    setup_requires=['setuptools_scm'],
    include_package_data=True,

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={},
)

