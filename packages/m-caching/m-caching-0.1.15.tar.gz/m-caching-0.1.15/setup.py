from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

version_dev='0.1.8'
version_prod='0.1.15'

run_mode=''

setup(name='m-caching' + run_mode,
      version='0.1.15',
      description='Setup normal class to mobio lru cache',
      url='',
      author='MOBIO',
      author_email='contact@mobio.io',
      license='MIT',
      packages=['mobio/libs/caching'],
      install_requires=["redis"],
      long_description=long_description,
      long_description_content_type='text/markdown')
