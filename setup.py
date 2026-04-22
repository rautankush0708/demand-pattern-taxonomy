from setuptools import setup, find_packages

setup(
    name="demand_taxonomy",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
    ],
    author="Demand Intelligence Team",
    description="A Python engine for the 12-Dimension Demand Pattern Taxonomy",
    url="https://github.com/rautankush0708/demand-pattern-taxonomy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
