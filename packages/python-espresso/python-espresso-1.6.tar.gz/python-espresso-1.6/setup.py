from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="python-espresso",
    version="1.6",
    description="A tiny type-safe expression parser in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aadvik P",
    author_email="aadv1k@outlook.com",
    url="https://github.com/aadv1k/python-espresso",
    license="MIT",
    packages=find_packages(),
    install_requires=[],
)
