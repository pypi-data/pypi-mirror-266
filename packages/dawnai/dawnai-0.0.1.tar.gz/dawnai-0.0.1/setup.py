from setuptools import setup, find_packages

setup(
    name="dawnai",
    version="0.0.1",
    description="Dawn (Python SDK)",
    author="Dawn",
    author_email="sdk@dawnai.com",
    long_description="For questions, email us at sdk@dawnai.com",
    long_description_content_type="text/markdown",
    url="https://dawnai.com",
    packages=find_packages(include=["dawn", "dawn.*", "tests", "tests.*"]),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
