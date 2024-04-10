from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pcy_algo',
    version='0.0.1',
    description='A package for implementing PCY algorithm in association rule mining',
    author= 'MuraliB',
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['association rule mining','apriori algorithm','pcy algorithm'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['PCY'],
    package_dir={'':'src'},
    install_requires = [
        'pandas'
    ]
)
