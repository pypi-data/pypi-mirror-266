from setuptools import setup, find_packages

import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='pypantera',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
    ],

    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/Kekkodf/pypantera",

    author="Francesco L. De Faveri",

    author_email="francescoluigi.defaveri@phd.unipd.it",

    keywords=["Differential Privacy", "NLP", "Obfuscation", "Anonymization"],

    project_urls={  # Optional
        "Bug Reports": "https://github.com/Kekkodf/pypantera/issues",
        #"Funding": "https://donate.pypi.org",
        #"Say Thanks!": "http://saythanks.io/to/example",
        "Source": "https://github.com/Kekkodf/pypantera",
    },
)