from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lxgrCounter",
    version="0.5",
    author="Kristopher Kyle",
    author_email="kristopherkyle1@gmail.com",
    description="Tag counting tool for LxGrTagger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kristopherkyle/tagCounter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"tagCounter": ["*.txt"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)