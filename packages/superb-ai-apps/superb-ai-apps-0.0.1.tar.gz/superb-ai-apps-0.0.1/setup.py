from setuptools import find_packages, setup


# Read requirements.txt and prepare it for the install_requires argument
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="superb-ai-apps",
    version="0.0.1",
    description="Python Package for Superb-AI Apps",
    install_requires=requirements,
    packages=find_packages(exclude=("tests*", "testing*")),
)
