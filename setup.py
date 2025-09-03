#!/usr/bin/env python3
"""
VirtualDisplayPy Setup Script
Date: 03/09/2025
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="virtualdisplaypy",
    version="1.0.0",
    author="MostaGare Development Team",
    author_email="dev@mostagare.com",
    description="Émulateur d'Afficheur Virtuel pour MostaGare",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mostagare/virtualdisplaypy",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yaml", "*.json"],
        "resources": ["*"],
        "config": ["*"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.2.0",
            "pytest-qt>=4.2.0", 
            "pytest-asyncio>=0.21.0",
            "black>=22.10.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "test": [
            "pytest>=7.2.0",
            "pytest-qt>=4.2.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "virtualdisplaypy=main:main",
            "vdpy=main:main",
        ],
        "gui_scripts": [
            "virtualdisplaypy-gui=main:main",
        ],
    },
    keywords=[
        "emulator", "display", "serial", "usb", "testing", "mostagare",
        "virtual", "hardware", "simulation", "qt", "gui"
    ],
    project_urls={
        "Bug Reports": "https://github.com/mostagare/virtualdisplaypy/issues",
        "Source": "https://github.com/mostagare/virtualdisplaypy",
        "Documentation": "https://github.com/mostagare/virtualdisplaypy/wiki",
    },
)