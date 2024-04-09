from setuptools import setup, find_packages

setup(
    name='verbolab',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        "wikipedia",
        "wget",
        "llama-cpp-python"
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)