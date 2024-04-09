from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = [r.strip() for r in f.readlines()]
setup(
    name='verbolab',
    version='0.0.1',
    packages=find_packages(),
    install_requires=required,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)