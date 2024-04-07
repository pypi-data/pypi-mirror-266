from setuptools import setup, find_packages

setup(
    name="nightshifttrader",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",  # Add other dependencies as needed
    ],
    author="Your Name",
    author_email="nightshiftdevv@gmail.com",
    description="A simple package to fetch stock prices",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nightshiftt/nightshifttrader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
