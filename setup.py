from setuptools import setup, find_packages

setup(
    name="pypakma",
    version="1.0.0",
    description="Physics Simulation and Measurement Data Acquisition Studio (Port of JPAKMA)",
    author="NCKH Research Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.6.0",
        "pyqtgraph>=0.13.0",
        "numpy>=1.25.0",
        "pyserial>=3.5",
    ],
    entry_points={
        "console_scripts": [
            "pypakma=main:main",
        ],
    },
    python_requires=">=3.10",
)
