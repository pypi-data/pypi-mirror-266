from setuptools import setup, find_packages

setup(
    name='ncpcs_common',
    version='1.1.3',
    packages=find_packages(),
    install_requires=[
        'pytest',
        'pymysql',
        'python-dateutil',
        'pytest',
        'cryptography'
    ]
)