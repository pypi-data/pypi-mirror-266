from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt") as f:
    requirements = f.read().splitlines()
with open("requirements-complete.txt") as f:
    complete = f.read().splitlines()
with open("requirements-dev.txt") as f:
    dev = f.read().splitlines()

complete = complete[1:]  # Remove reference to requirements file
dev = dev[1:]  # Remove reference to requirement-complete file

setup(
    name="besos",
    version="2.2.2",
    description="A library for Building and Energy Simulation, Optimization and Surrogate-modelling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ralph Evins",
    author_email="revins@uvic.ca",
    url="https://gitlab.com/energyincities/besos",
    packages=["besos"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    extras_require={
        "complete": complete,
        "dev": dev,
    },
)
