from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="reddit-data-pipeline",
    version="0.1.0",
    author="Noshik Chowdary",
    author_email="your.email@example.com",
    description="A modern data pipeline for Reddit data processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/noshikchowdary/DE_Reddit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "reddit-pipeline=reddit_pipeline.cli:main",
        ],
    },
) 