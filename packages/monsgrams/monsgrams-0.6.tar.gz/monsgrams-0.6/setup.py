from setuptools import setup, find_packages

setup(
    name='monsgrams',
    version='0.6',
    description='A simple Python library for creating telegram bot.',
    author='grubx64',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    license="MIT",
    packages=find_packages(),
)