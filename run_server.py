#!/usr/bin/env python3
"""
Quick runner script for the Sargoth Mermaid MCP Server

Usage:
    python run_server.py [--api-url http://localhost:5000]
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the server
from mcp_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main()) 