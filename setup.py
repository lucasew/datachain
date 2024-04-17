from setuptools import find_packages, setup
from pathlib import Path

setup(
    name="datachain",
    version=(Path(__file__).parent / "datachain" / "VERSION").read_text(),
    description="Small-data library that may become something",
    url="https://github.com/lucasew/datachain",
    author="lucasew",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=[]
)
