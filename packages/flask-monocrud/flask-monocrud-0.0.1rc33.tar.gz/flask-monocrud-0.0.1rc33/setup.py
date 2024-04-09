from setuptools import setup, find_packages



with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="flask-monocrud",
    version="0.0.1rc33",
    author="Jarriq Rolle",
    author_email="jrolle@bnbbahamas.com",
    description="Package provides utilities for managing fixture data python applications. It offers a convenient way to populate database tables with predefined data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JarriqTheTechie/flask-monocrud",
    packages=['flask_monocrud'],
    package_data={'flask_monocrud': ['**/*']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        "flask",
        "flask-orphus",
        "flask_wtf",
        "masonite-orm",
        "pyyaml",
        "orjson",
        "ward",
        "currencies",
        "packaging"
    ],
)
