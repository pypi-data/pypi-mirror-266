from setuptools import setup, find_packages

setup(
    name='monsgrams',
    version='1.1',
    description='A simple Python library for creating telegram bot.',
    author='grubx64',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    license="MIT",
    url="https://github.com/tech-voyager/monsgrams/",
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.9.3'
    ],
)
