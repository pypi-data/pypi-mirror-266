import pathlib

import setuptools

setuptools.setup(
    name="searchailib",
    version="0.1.0",
    description="Fundamentals functions for azure search ai",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://www.pomiager.com",
    author="Sandro Vecchiarelli",
    author_email="sandro.vecchiarelli@pomiager.com",
    license="The Unlicense",
    project_urls={
        "Documentation":"https://www.pomiager.com",
        "Source":"https://github.com/pomiagerdev/searchailib",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities"       
    ],
    python_requires=">=3.10, <3.12",
    install_requires=["requests", "pandas >= 2.0"],
    
    packages=setuptools.find_namespace_packages(),
    include_package_data=True,
    entry_points={"console_scripts":["searchailib = searchailib.cli:main"]}
    
    
)