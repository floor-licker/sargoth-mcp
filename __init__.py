"""
Sargoth Mermaid Renderer - MCP Server

A Model Context Protocol (MCP) server that exposes the Sargoth Mermaid Renderer API
as tools that AI assistants can use to generate beautiful diagrams during conversations.
"""

__version__ = "1.0.0"
__author__ = "Sargoth Team"
__description__ = "MCP Server for Mermaid Diagram Generation"

from .mcp_server import MermaidMCPServer

__all__ = ["MermaidMCPServer"] 