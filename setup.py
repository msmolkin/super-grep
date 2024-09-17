from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("SUPPORT.md", "r", encoding="utf-8") as fh:
    support_info = fh.read()

setup(
    name="super-grep",
    version="0.1.5",
    author="Michael Smolkin",
    author_email="michael@smolkin.org",
    description="A powerful, format-agnostic search tool",
    long_description=long_description + "\n\n" + support_info,
    long_description_content_type="text/markdown",
    url="https://github.com/msmolkin/super-grep",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "super-grep=super_grep.main:main",
        ],
    },
    package_data={
        "": ["SUPPORT.md"],
    },
)