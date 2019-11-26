from typing import List, Dict, Any
from setuptools import setup, find_packages

VERSION: Dict[str, Any] = {}
with open("registrable/version.py", "r") as version_file:
    exec(version_file.read(), VERSION)


def read_reqs_file(path: str) -> List[str]:
    reqs: List[str] = []
    with open(path, "r") as reqs_file:
        for line in reqs_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            reqs.append(line)
    return reqs


setup(
    name="registrable",
    version=VERSION["VERSION"],
    description="Python module for registering and instantiating classes by name. "
    "Based on the implementation from AllenNLP.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/epwalsh/python-registrable",
    license="Apache 2.0",
    author="Evan Pete Walsh",
    author_email="epwalsh10@gmail.com",
    packages=find_packages(exclude=["registrable.tests.*", "tests"]),
    install_requires=read_reqs_file("requirements.txt"),
    tests_require=read_reqs_file("requirements.dev.txt"),
    python_requires=">=3.6.1",
)
