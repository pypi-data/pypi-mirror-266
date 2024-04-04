from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='pypanter',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
    ],

    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/Kekkodf/pypanter",

    author="Francesco L. De Faveri",

    author_email="francescoluigi.defaveri@phd.unipd.it",

    keywords=["Differential Privacy", "NLP", "Obfuscation", "Anonymization"],

    project_urls={  # Optional
        "Bug Reports": "https://github.com/Kekkodf/pypanter/issues",
        #"Funding": "https://donate.pypi.org",
        #"Say Thanks!": "http://saythanks.io/to/example",
        "Source": "https://github.com/Kekkodf/pypanter",
    },
)