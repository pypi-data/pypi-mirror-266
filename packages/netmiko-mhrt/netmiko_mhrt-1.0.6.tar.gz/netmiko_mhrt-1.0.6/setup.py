import setuptools
import os
from subprocess import check_output


version = "1.0.6"


with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().split("\n")

setuptools.setup(
    name="netmiko_mhrt",
    version=version,
    author="Felix Li",
    author_email="immphoenix@gmail.com",
    description="a forked version of netmiko_multihop",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/1mmortalPhoenix/netmiko_mhrt",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={"": ["*"]},
    install_requires=install_requires,
    license="ASL V2",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    zip_safe=False,
)
