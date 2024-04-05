from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="langvec",
    version="0.0.2",
    author="Simeon Emanuilov",
    author_email="simeon.emanuilov@gmail.com",
    description="Language of Vectors (LangVec) is a simple Python library designed for transforming numerical vector data into a language-like structure using a predefined set of words (lexicon).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=["langvec"],
    python_requires=">=3.00",
    install_requires=[
        "numpy"
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="langvec semantic search vectorization",
)
