#!/usr/bin/env python3
"""Setup script for MSR605X Utility."""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="msr605x-utility",
    version="1.0.0",
    author="Samuele Quaranta",
    author_email="samuelequaranta@example.com",
    description="MSR605X Magnetic Stripe Card Reader/Writer utility for Ubuntu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sam4000133/msr605x-ubuntu",
    project_urls={
        "Bug Tracker": "https://github.com/Sam4000133/msr605x-ubuntu/issues",
        "Source Code": "https://github.com/Sam4000133/msr605x-ubuntu",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: System :: Hardware",
    ],
    packages=find_packages(include=["src", "src.*"]),
    package_dir={"": "."},
    python_requires=">=3.10",
    install_requires=[
        "PyGObject>=3.44.0",
        "hidapi>=0.14.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "msr605x=src.main:main",
        ],
        "gui_scripts": [
            "msr605x-gui=src.main:main",
        ],
    },
    data_files=[
        ("share/applications", ["data/com.github.msr605x.desktop"]),
        ("share/icons/hicolor/scalable/apps", ["data/com.github.msr605x.svg"]),
        ("share/msr605x", ["data/style.css"]),
        ("lib/udev/rules.d", ["data/99-msr605x.rules"]),
    ],
    include_package_data=True,
    zip_safe=False,
)
