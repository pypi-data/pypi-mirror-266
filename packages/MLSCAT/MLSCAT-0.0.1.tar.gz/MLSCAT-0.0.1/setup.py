from setuptools import setup, find_packages

with open('./README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='MLSCAT',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
    ],
    author="i4mhmh",
    author_email='i4mhmh@outlook.com',
    description='A small cat help you enjoy your side channel attack journal!',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires = ">=3.8"
)