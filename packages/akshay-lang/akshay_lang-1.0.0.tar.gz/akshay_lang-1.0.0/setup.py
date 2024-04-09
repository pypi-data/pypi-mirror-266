from setuptools import setup, find_packages

setup(
    name='akshay_lang',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.0',
        'pandas>=1.0',
    ],
)
