from setuptools import setup, find_packages

setup(
    name="afas_connector",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        'requests >= 2.31.0',
        'python-dotenv >= 1.0.1'
    ],
    author="Robin Bakker",
    author_email="robin@bakeable.nl",
    description="AfasConnector is a Python package that simplifies interacting with AFAS Connectors via HTTP requests. It provides classes for making GET, POST, and PUT requests to AFAS Connectors and handling their responses.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/bakeable/afas-connector",
    license="MIT",
    classifiers=[
        # Trove classifiers (https://pypi.org/classifiers/)
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
