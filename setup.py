#!/usr/bin/env python3
"""
Setup script for Sargoth Mermaid Renderer MCP Server
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sargoth-mermaid-mcp-server",
    version="1.0.0",
    author="Sargoth Team",
    author_email="team@sargoth.dev",
    description="MCP Server for Mermaid Diagram Generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sargoth/mermaid-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mermaid-mcp-server=mcp_server:main",
        ],
    },
    keywords="mcp model-context-protocol mermaid diagrams ai assistant",
    project_urls={
        "Bug Reports": "https://github.com/sargoth/mermaid-mcp-server/issues",
        "Source": "https://github.com/sargoth/mermaid-mcp-server",
        "Documentation": "https://github.com/sargoth/mermaid-mcp-server/blob/main/README.md",
    },
) 