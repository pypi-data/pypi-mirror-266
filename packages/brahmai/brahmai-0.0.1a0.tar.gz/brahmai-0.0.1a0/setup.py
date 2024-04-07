from setuptools import setup, find_packages

setup(
    name="brahmai",
    version="0.0.1-alpha",
    author="BRAHMAI",
    author_email="hello@brahmai.in",
    packages=find_packages(),
    description="Python SDK to interact with BRAHMAI APIs.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[],
    python='>=3.7'
)