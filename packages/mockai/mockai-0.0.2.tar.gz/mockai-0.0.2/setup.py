from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'MockAI is a library that allows you to mock AI responses using custom commands suitable for simulating responses during testing without AI inference cost.'

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='mockai',
    version=VERSION,
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Felix Künnecke",
    author_email="kuenneckefelix@gmail.com",
    url="https://github.com/chefkoch24/mockai",
    packages=find_packages(),
    install_requires=[

    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities"
    ],
    extras_require={
       "dev":["twine>=5.0.0",  "pytest>=8.1.1"]
    }
)
