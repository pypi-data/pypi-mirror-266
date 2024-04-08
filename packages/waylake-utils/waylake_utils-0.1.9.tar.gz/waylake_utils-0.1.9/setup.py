from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='waylake_utils',
    version='0.1.9',
    packages=find_packages(),
    description='Custom logging utility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='waylake',
    author_email='plmokn7034soo@icloud.com',
)
