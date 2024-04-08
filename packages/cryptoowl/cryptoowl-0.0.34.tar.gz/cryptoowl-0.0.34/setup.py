from setuptools import setup, find_packages

with open("./README.md") as readme:
    long_description = readme.read()

setup(
    name="cryptoowl",
    version="0.0.34",
    author="Cryptoowl",
    author_email="cryptoowl.app@gmail.com",
    description="A library, that stores commonly used code for different modules in the CryptoOwl application",
    long_description=long_description,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pytz~=2023.3",
        "boto3~=1.26.104",
        "PyMySQL~=1.0.3",
        "redis~=5.0.3",
        "botocore~=1.29.104",
        "setuptools~=58.0.4",
        "pymemcache==4.0.0",
        "psycopg2-binary==2.9.9",
        "requests==2.31.0"
    ],
)
