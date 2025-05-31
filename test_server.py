#!/usr/bin/env python3
"""
Test script for the Mermaid MCP Server

This script tests the MCP server functionality by directly calling the methods
without going through the MCP protocol (useful for debugging).
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import mcp_server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import MermaidMCPServer


async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing Mermaid MCP Server")
    print("=" * 50)
    
    # Initialize the server
    server = MermaidMCPServer()
    
    # Test data
    test_code = """graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B"""
    
    print("📝 Test Mermaid Code:")
    print(test_code)
    print()
    
    # Test 1: Validate Mermaid
    print("🔍 Test 1: Validating Mermaid syntax...")
    try:
        result = await server._validate_mermaid({"code": test_code})
        print(f"✅ Validation Result: {result[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    print()
    
    # Test 2: Suggest improvements
    print("💡 Test 2: Getting suggestions...")
    try:
        result = await server._suggest_improvements({"code": test_code})
        print(f"✅ Suggestions Result: {result[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Suggestions failed: {e}")
    print()
    
    # Test 3: Render SVG
    print("🎨 Test 3: Rendering SVG...")
    try:
        result = await server._render_svg({"code": test_code, "theme": "modern"})
        print(f"✅ SVG Result: {result[0].text[:200]}...")
    except Exception as e:
        print(f"❌ SVG rendering failed: {e}")
    print()
    
    # Test 4: Render PNG
    print("🖼️ Test 4: Rendering PNG...")
    try:
        result = await server._render_png({"code": test_code, "theme": "modern", "scale": 2})
        print(f"✅ PNG Result: {result[0].text[:200]}...")
    except Exception as e:
        print(f"❌ PNG rendering failed: {e}")
    print()
    
    print("✨ MCP Server testing complete!")


async def test_helper_methods():
    """Test helper methods"""
    print("\n🔧 Testing Helper Methods")
    print("=" * 50)
    
    server = MermaidMCPServer()
    
    # Test diagram type detection
    test_cases = [
        ("graph TD\nA --> B", "flowchart"),
        ("sequenceDiagram\nA->>B: Hello", "sequence"),
        ("classDiagram\nclass Animal", "class"),
        ("gantt\ntitle Project", "gantt"),
        ("pie title Fruits\n\"Apple\": 50", "pie"),
    ]
    
    print("🔍 Testing diagram type detection:")
    for code, expected in test_cases:
        detected = server._detect_diagram_type(code)
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{code.split()[0]}' -> detected: {detected}, expected: {expected}")
    
    print("\n📏 Testing complexity estimation:")
    complexity_cases = [
        ("A --> B", "Low"),
        ("graph TD\n" + "\n".join([f"A{i} --> B{i}" for i in range(15)]), "High"),
        ("graph TD\n" + "\n".join([f"A{i} --> B{i}" for i in range(8)]), "Medium"),
    ]
    
    for code, expected in complexity_cases:
        complexity = server._estimate_complexity(code)
        status = "✅" if complexity == expected else "❌"
        print(f"{status} {len(code.splitlines())} lines -> {complexity} (expected: {expected})")


if __name__ == "__main__":
    print("🚀 Starting MCP Server Tests")
    print("Make sure your Mermaid API is running on http://localhost:5000")
    print()
    
    # Test helper methods first (no API required)
    asyncio.run(test_helper_methods())
    
    # Test API-dependent methods
    try:
        asyncio.run(test_mcp_server())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Make sure the Mermaid API is running and accessible")
        sys.exit(1) 