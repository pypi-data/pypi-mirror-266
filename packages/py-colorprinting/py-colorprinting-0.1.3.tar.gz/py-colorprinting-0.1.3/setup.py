from setuptools import setup, find_packages

setup(
    name="py-colorprinting",
    version="0.1.3",
    packages=find_packages(),
    license="MIT",
    description="Print colored text in python!",
    long_description=open('README.md').read(),
    author="Arpaia",
    author_email="raf@arpaiacorp.com",
    url="",
    install_requires=[
        "requests>=2.25.0,<3.0.0"
    ],
)
