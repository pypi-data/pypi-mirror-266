"""The setup script."""

from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

install_requirements = [
    "scipy",
    "scikit-bio",
    "pandas",
    "numpy",
    "plotly",
    "jinja2",
    "rich",
    "rich-click",
    "click-option-group",
    "frictionless>=4.32.0, <5",
]

test_requirements = [
    "pytest>=3",
]

# Docs reqs

extra_requirements = [
    "mkdocs",
    "mkdocstrings",
    "mkdocstrings.python",
    "click",
    "wheel",
    "twine",
]

setup(
    author="João Vitor F. Cavalcante",
    author_email="jvfe@ufrn.edu.br",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.8",
        "Natural Language :: English",
    ],
    description="Generate reports from metagenomics data",
    install_requires=install_requirements,
    license="BSD license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    entry_points={"console_scripts": ["microview = microview.cli:main"]},
    keywords="metagenomics workflow visualization report",
    name="MicroView",
    packages=find_packages(include=["microview", "microview.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    extras_require={"dev": extra_requirements},
    url="https://github.com/jvfe/microview",
    project_urls={
        "Bug Tracker": "https://github.com/jvfe/microview/issues",
        "Documentation": "https://jvfe.github.io/microview/",
        "Source Code": "https://github.com/jvfe/microview",
    },
    version="0.10.1",
    zip_safe=False,
)
