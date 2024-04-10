from setuptools import setup, find_packages

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='velikafkaclient',
    version='1.1.18',
    description='Veli Kafka Client',
    author='Konstantine',
    author_email='kdvalishvili@veli.store',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages()
)
