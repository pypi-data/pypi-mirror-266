from setuptools import setup


setup(
    name='salure_helpers_datev',
    version='1.0.5',
    description='Datev wrapper from Salure',
    long_description='Datev wrapper from Salure',
    author='D&A Salure',
    author_email='support@salureconnnect.com',
    packages=["salure_helpers.datev"],
    license='Salure License',
    install_requires=[
        'salure-helpers-salureconnect>=1',
        'salure-helpers-salure-functions>=0',
        'pandas>=1,<=3'
    ],
    zip_safe=False,
)