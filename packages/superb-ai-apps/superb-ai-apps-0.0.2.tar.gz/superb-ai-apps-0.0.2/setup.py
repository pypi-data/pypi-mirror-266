from setuptools import find_packages, setup
import os

# Determine the directory containing this file
setup_dir = os.path.dirname(os.path.abspath(__file__))

# Use the directory to build the path to requirements.txt
requirements_path = os.path.join(setup_dir, "requirements.txt")

# Read requirements.txt and prepare it for the install_requires argument
with open(requirements_path) as f:
    requirements = f.read().splitlines()

setup(
    name="superb-ai-apps",
    version="0.0.2",
    description="Python Package for Superb-AI Apps",
    install_requires=requirements,
    packages=find_packages(exclude=("tests*", "testing*")),
)
