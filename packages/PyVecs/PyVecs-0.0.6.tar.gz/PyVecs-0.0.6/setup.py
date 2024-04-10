from setuptools import setup, find_packages

from pathlib import Path

setup(
    name="PyVecs",
    version="0.0.6",
    author="Thales Rodrigues",
    author_email="thaleshend@gmail.com",
    description="A simple 2D and 3D Vector class to Python.",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],
    project_urls={
        "Github": "https://github.com/Thales625/PyVecs",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities"
    ],
    python_requires=">=3.10,<=3.12.2"
)
