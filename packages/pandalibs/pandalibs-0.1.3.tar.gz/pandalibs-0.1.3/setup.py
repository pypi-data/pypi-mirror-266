from setuptools import find_packages, setup

setup(
    name="pandalibs",
    packages=find_packages(include=["pandalibs"]),
    version="0.1.3",
    description="My personal library.",
    author="nightpanda2810",
    install_requires=["pyyaml"],
    setup_requires=[],
    tests_require=[],
    test_suite="tests",
)

# How to run:
# python .\setup.py bdist_wheel
