from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='jsonex',
    version='1.1',
    description='Json library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Krzysztof Żyłka',
    install_requires=[],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)