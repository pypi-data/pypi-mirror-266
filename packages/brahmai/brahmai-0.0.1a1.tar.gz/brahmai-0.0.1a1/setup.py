from setuptools import setup, find_packages

setup(
    name="brahmai",
    version="0.0.1-alpha-1",
    author="BRAHMAI",
    author_email="hello@brahmai.in",
    packages=find_packages(),
    install_requires=[
        "spacy-loggers==1.0.5",
        "transformers==4.39.2",
        "tldextract==5.1.2",
        "phonenumbers==8.13.33",
        "cryptography==42.0.5",
        "pycryptodome==3.20.0",
        "spacy-huggingface-pipelines==0.0.4"
    ],
    description="Python SDK to interact with BRAHMAI APIs.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    python='>=3.7'
)