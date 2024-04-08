from setuptools import setup, find_packages

setup(
    name='json_csv_file_converter',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'boto3>=1.34.78',
        'requests>=2.31.0'
    ]
)
