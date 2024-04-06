from setuptools import setup, find_packages

setup(
    name="vectara-cli",
    version="0.1.0",
    author="Tonic-AI",
    author_email="team@tonic-ai.com",
    description="A CLI tool for interacting with the Vectara platform, including advanced text processing and indexing features.",
    long_description=open('README.md').read(),
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
        ],
    },
    entry_points={
        'console_scripts': [
            'vectara-cli=vectara_cli.main:main',  # Ensure you have a main.py with a main function in your vectara_cli package
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
    python_requires='>=3.6',
    license="MIT",
)
