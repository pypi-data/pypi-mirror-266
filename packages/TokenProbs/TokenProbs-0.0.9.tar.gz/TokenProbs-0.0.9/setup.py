from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.9'
DESCRIPTION = 'Extract token-level probabilities from LLMs for classification-type outputs.'
LONG_DESCRIPTION = 'A package that allows one to extract token-level probabilities. This method can be used for example to extract sentiment class probabilities or other probability-based queries instead of parsing text-generation outputs.'

# Setting up
setup(
    name="TokenProbs",
    version=VERSION,
    author="Francesco A. Fabozzi",
    author_email="francescoafabozzi@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    package_dir={"":"src"},
    packages=find_packages(where="src"),
    install_requires=['bitsandbytes', 'datasets', 'accelerate', 'loralib', 'transformers','peft','trl'],
    keywords=['python', 'LLMs', 'finance', 'forecasting', 'language models', 'huggingface'],
    classifiers=[
        "Development Status :: 1 - Planning"
    ]
)

