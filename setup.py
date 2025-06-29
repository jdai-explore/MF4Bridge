"""
MF4Bridge Setup Script
Installation and packaging configuration
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "MF4Bridge - MDF4 File Converter"

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    requirements.append(line)
    
    return requirements

setup(
    name="mf4bridge",
    version="1.0.0",
    author="MF4Bridge Team",
    author_email="support@mf4bridge.com",
    description="Convert MDF4 files to ASC, CSV, and TRC formats",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mf4bridge/mf4bridge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "pyinstaller>=5.0.0",
        ],
        "enhanced": [
            "lz4>=4.0.0",
            "pandas>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "mf4bridge=main:main",
        ],
        "gui_scripts": [
            "mf4bridge-gui=main:main",
        ]
    },
    include_package_data=True,
    package_data={
        "": ["*.ico", "*.png", "*.jpg", "*.txt", "*.md"],
    },
    zip_safe=False,
    keywords=[
        "mdf4", "canbus", "automotive", "converter", "asc", "csv", "trc",
        "vector", "peak", "canoe", "canalyzer", "pcan", "measurement",
        "data", "logging", "analysis"
    ],
    project_urls={
        "Bug Reports": "https://github.com/mf4bridge/mf4bridge/issues",
        "Source": "https://github.com/mf4bridge/mf4bridge",
        "Documentation": "https://mf4bridge.readthedocs.io/",
    },
)