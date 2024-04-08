# ./setup.py

from setuptools import setup, find_packages

setup(
    name="vectara-cli",
    version="0.1.9",
    author="Tonic-AI",
    author_email="team@tonic-ai.com",
    description="A CLI tool for interacting with the Vectara platform, including advanced text processing and indexing features.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://git.tonic-ai.com/releases/vectara-cli",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    extras_require={
        "advanced": [
            "accelerate",
            "torch>=1.8.0",
            "transformers>=4.5.0",
            "span_marker",
            "spacy",
        ],
    },
    entry_points={
        "console_scripts": [
            "vectara=vectara_cli.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    license="MIT",
    keywords="vectara search-engine document-indexing text-analysis information-retrieval natural-language-processing cli-tool data-science machine-learning text-processing",
)
