from setuptools import find_packages, setup

setup(
    name="AppWrapper",
    version="0.2.12",
    description="Library for Superb-AI Apps",
    install_requires=["requests>=2.0.0", "boto3>=1.13.4"],
    packages=find_packages(exclude=("tests*", "testing*")),
)
