import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setuptools.setup(
    name="Temperatur_Nu",
    version="0.0.1",
    author="Patrik Johansson",
    author_email="github@popeen.com",
    description="Get and or publish temperatures to temperatur.nu",
    long_description="Get and or publish temperatures to temperatur.nu",
    long_description_content_type="text/markdown",
    url="https://github.com/popeen/PyPi-Temperatur_Nu",
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)