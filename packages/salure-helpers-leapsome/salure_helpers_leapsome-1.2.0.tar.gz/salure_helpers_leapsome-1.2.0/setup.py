from setuptools import setup

setup(
    name='salure_helpers_leapsome',
    version='1.2.0',
    description='Leapsome wrapper from Salure',
    long_description='Leapsome wrapper from Salure',
    author='D&A Salure',
    author_email='support@salureconnnect.com',
    packages=["salure_helpers.leapsome"],
    license='Salure License',
    install_requires=[
        'salure-helpers-salureconnect>=1',
        'pandas>=2,<3',
        'openpyxl>=3,<4',
        'paramiko>=3,<4',
        'pysftp==0.2.9'
    ],
    zip_safe=False,
)
