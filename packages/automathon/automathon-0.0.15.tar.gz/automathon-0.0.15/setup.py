from setuptools import find_packages, setup

# read the contents of the README file
from os import path

thisDirectory = path.abspath(path.dirname(__file__))
with open(path.join(thisDirectory, "README.md"), encoding="utf-8") as f:
    longDescription = f.read()

setup(
    name="automathon",
    packages=find_packages(
        include=["automathon", "automathon.finiteAutomata", "automathon.errors"]
    ),
    include_package_data=True,
    version="v0.0.15",
    description="A Python library for simulating and visualizing finite automata",
    long_description=longDescription,
    long_description_content_type="text/markdown",
    author="Robin Hafid Quintero Lopez",
    license="MIT",
    install_requires=["graphviz==0.16"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest==4.4.1", "graphviz==0.16"],
    test_suite="tests",
    author_email="rohaquinlop301@gmail.com",
    url="https://github.com/rohaquinlop/automathon",
    download_url="https://github.com/rohaquinlop/automathon/archive/refs/tags/v0.0.15.tar.gz",
    keywords=["python", "automata", "automata", "automathon"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
