from setuptools import setup, find_packages

PKG = "ticketsdk"
version = "2.2.3"
long_desc = (
    """This SDK is a programatic inteface into the ticket APIs of NandH Logistics."""
)

setup(
    name=PKG,
    version=version,
    description="ticket SDK for Python",
    author="it@nandhlogistics.vn",
    author_email="it@nandhlogistics.vn",
    url="https://github.com/ITNHL/nh-ticket-sdk",
    license="Version 1.0",
    packages=find_packages(include=["ticketsdk", "ticketsdk.*"]),
    provides=[PKG],
    test_suite="tests",
    long_description=long_desc,
    install_requires=[
        "pre-commit==3.6.2",
        "marshmallow==3.19.0",
        "requests==2.31.0",
    ],
    dependency_links=["file:dist/ticketsdk-2.2.1.tar.gz"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
    ],
)
