from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="datachain",
    version=(Path(__file__).parent / "datachain" / "VERSION").read_text(),
    description="Small-data library that may become something",
    url="https://github.com/lucasew/datachain",
    author="lucasew",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=[
        "pynacl",
    ],
    extras_require={
        "test": ["pytest"],
    },
)
