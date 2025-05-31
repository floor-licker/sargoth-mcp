#!/usr/bin/env python3
"""
MCP Server for Sargoth Mermaid Renderer

This server exposes the Mermaid rendering API as MCP tools that AI assistants can use
to generate beautiful diagrams during conversations.
"""

import asyncio
import json
import base64
from typing import Any, Dict, List, Optional
import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types


class MermaidMCPServer:
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        self.api_base_url = api_base_url.rstrip('/')
        self.server = Server("mermaid-renderer")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="render_mermaid_svg",
                    description="Generate an SVG diagram from Mermaid code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The Mermaid diagram code to render"
                            },
                            "theme": {
                                "type": "string",
                                "description": "Theme for the diagram",
                                "enum": ["modern", "classic", "dark", "minimal"],
                                "default": "modern"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                types.Tool(
                    name="render_mermaid_png",
                    description="Generate a PNG image from Mermaid code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The Mermaid diagram code to render"
                            },
                            "theme": {
                                "type": "string",
                                "description": "Theme for the diagram",
                                "enum": ["modern", "classic", "dark", "minimal"],
                                "default": "modern"
                            },
                            "scale": {
                                "type": "integer",
                                "description": "PNG scale factor (1-4)",
                                "minimum": 1,
                                "maximum": 4,
                                "default": 2
                            }
                        },
                        "required": ["code"]
                    }
                ),
                types.Tool(
                    name="validate_mermaid",
                    description="Validate Mermaid diagram syntax by attempting to render it",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The Mermaid diagram code to validate"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                types.Tool(
                    name="suggest_mermaid_improvements",
                    description="Analyze Mermaid code and suggest improvements or fixes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The Mermaid diagram code to analyze"
                            },
                            "diagram_type": {
                                "type": "string",
                                "description": "Expected diagram type",
                                "enum": ["flowchart", "sequence", "class", "state", "gantt", "pie", "journey", "git"]
                            }
                        },
                        "required": ["code"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls"""
            
            try:
                if name == "render_mermaid_svg":
                    return await self._render_svg(arguments)
                elif name == "render_mermaid_png":
                    return await self._render_png(arguments)
                elif name == "validate_mermaid":
                    return await self._validate_mermaid(arguments)
                elif name == "suggest_mermaid_improvements":
                    return await self._suggest_improvements(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def _render_svg(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Render Mermaid code to SVG"""
        code = arguments["code"]
        theme = arguments.get("theme", "modern")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/api/render/svg",
                json={"code": code, "theme": theme},
                timeout=30.0
            )
            
            if response.status_code == 200:
                svg_content = response.text
                # Return both the SVG content and a success message
                return [
                    types.TextContent(
                        type="text",
                        text=f"✅ SVG diagram generated successfully! ({len(svg_content)} characters)\n\n"
                             f"Theme: {theme}\n"
                             f"The SVG can be saved to a file or embedded directly in HTML.\n\n"
                             f"SVG Content:\n```svg\n{svg_content}\n```"
                    )
                ]
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"error": response.text}
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to render SVG: {error_data.get('error', 'Unknown error')}"
                )]

    async def _render_png(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Render Mermaid code to PNG"""
        code = arguments["code"]
        theme = arguments.get("theme", "modern")
        scale = arguments.get("scale", 2)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/api/render/png",
                json={"code": code, "theme": theme, "scale": scale},
                timeout=30.0
            )
            
            if response.status_code == 200:
                png_data = response.content
                png_size_kb = len(png_data) / 1024
                
                # Encode PNG as base64 for display
                png_base64 = base64.b64encode(png_data).decode()
                
                return [
                    types.TextContent(
                        type="text",
                        text=f"✅ PNG diagram generated successfully! ({png_size_kb:.1f} KB)\n\n"
                             f"Theme: {theme}\n"
                             f"Scale: {scale}x\n"
                             f"The PNG can be saved to a file or displayed in applications that support base64 images.\n\n"
                             f"To save this PNG, decode the base64 data below:\n\n"
                             f"```base64\n{png_base64}\n```\n\n"
                             f"Or use this data URL in HTML:\n"
                             f"```html\n<img src=\"data:image/png;base64,{png_base64}\" alt=\"Mermaid Diagram\">\n```"
                    )
                ]
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"error": response.text}
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to render PNG: {error_data.get('error', 'Unknown error')}"
                )]

    async def _validate_mermaid(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Validate Mermaid syntax by attempting to render"""
        code = arguments["code"]
        
        # Try to render as SVG (lightest option) to validate
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/api/render/svg",
                json={"code": code, "theme": "modern"},
                timeout=15.0
            )
            
            if response.status_code == 200:
                # Detect diagram type from the code
                diagram_type = self._detect_diagram_type(code)
                
                return [
                    types.TextContent(
                        type="text",
                        text=f"✅ Mermaid syntax is valid!\n\n"
                             f"Detected diagram type: {diagram_type}\n"
                             f"The diagram can be rendered successfully.\n\n"
                             f"Code analysis:\n"
                             f"- Lines: {len(code.splitlines())}\n"
                             f"- Characters: {len(code)}\n"
                             f"- Estimated complexity: {self._estimate_complexity(code)}"
                    )
                ]
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"error": response.text}
                return [types.TextContent(
                    type="text",
                    text=f"❌ Mermaid syntax is invalid!\n\n"
                         f"Error: {error_data.get('error', 'Unknown error')}\n\n"
                         f"Common issues to check:\n"
                         f"- Proper diagram type declaration (graph, sequenceDiagram, etc.)\n"
                         f"- Correct arrow syntax (-->, ->>)\n"
                         f"- Balanced brackets and quotes\n"
                         f"- Valid node and edge definitions"
                )]

    async def _suggest_improvements(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Analyze Mermaid code and suggest improvements"""
        code = arguments["code"]
        diagram_type = arguments.get("diagram_type")
        
        # Detect diagram type if not provided
        if not diagram_type:
            diagram_type = self._detect_diagram_type(code)
        
        suggestions = []
        
        # Analyze the code
        lines = code.strip().splitlines()
        
        # Basic syntax checks
        if not lines:
            suggestions.append("- Code is empty. Add a diagram type declaration.")
        elif not any(line.strip().startswith(('graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'gantt', 'pie', 'journey', 'gitGraph')) for line in lines):
            suggestions.append("- Missing diagram type declaration. Start with 'graph TD', 'sequenceDiagram', etc.")
        
        # Check for common issues
        if 'graph' in code and 'TD' not in code and 'LR' not in code and 'TB' not in code and 'RL' not in code:
            suggestions.append("- Consider specifying graph direction: TD (top-down), LR (left-right), etc.")
        
        # Check for styling opportunities
        if len(lines) > 5 and 'class' not in code and 'style' not in code:
            suggestions.append("- Consider adding styling with classes or style definitions for better visual appeal")
        
        # Check for complexity
        complexity = self._estimate_complexity(code)
        if complexity == "High":
            suggestions.append("- High complexity detected. Consider breaking into multiple smaller diagrams")
        
        # Diagram-specific suggestions
        if diagram_type == "flowchart":
            if '-->' not in code and '---' not in code:
                suggestions.append("- Use arrows (-->) to connect flowchart nodes")
            if '{' not in code and '[' not in code and '(' not in code:
                suggestions.append("- Use different node shapes: [] for rectangles, {} for diamonds, () for circles")
        
        elif diagram_type == "sequence":
            if 'participant' not in code:
                suggestions.append("- Define participants explicitly for cleaner sequence diagrams")
            if 'note' not in code:
                suggestions.append("- Consider adding notes to clarify important interactions")
        
        # If no issues found
        if not suggestions:
            suggestions.append("- Code looks good! Consider experimenting with themes for different visual styles")
        
        return [
            types.TextContent(
                type="text",
                text=f"📊 Mermaid Code Analysis\n\n"
                     f"Diagram Type: {diagram_type}\n"
                     f"Complexity: {complexity}\n"
                     f"Lines: {len(lines)}\n\n"
                     f"💡 Suggestions for improvement:\n" + "\n".join(suggestions) + "\n\n"
                     f"🎨 Available themes: modern, classic, dark, minimal\n"
                     f"📐 Supported diagram types: flowchart, sequence, class, state, gantt, pie, journey, git"
            )
        ]

    def _detect_diagram_type(self, code: str) -> str:
        """Detect the type of Mermaid diagram"""
        code_lower = code.lower().strip()
        
        if code_lower.startswith('sequencediagram'):
            return "sequence"
        elif code_lower.startswith('classdiagram'):
            return "class"
        elif code_lower.startswith('statediagram'):
            return "state"
        elif code_lower.startswith('gantt'):
            return "gantt"
        elif code_lower.startswith('pie'):
            return "pie"
        elif code_lower.startswith('journey'):
            return "journey"
        elif code_lower.startswith('gitgraph'):
            return "git"
        elif code_lower.startswith('graph') or code_lower.startswith('flowchart'):
            return "flowchart"
        else:
            return "unknown"

    def _estimate_complexity(self, code: str) -> str:
        """Estimate diagram complexity"""
        lines = len(code.splitlines())
        chars = len(code)
        
        if lines > 20 or chars > 1000:
            return "High"
        elif lines > 10 or chars > 500:
            return "Medium"
        else:
            return "Low"

    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mermaid-renderer",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server for Mermaid Renderer")
    parser.add_argument(
        "--api-url",
        default="http://localhost:5000",
        help="Base URL of the Mermaid rendering API"
    )
    
    args = parser.parse_args()
    
    server = MermaidMCPServer(api_base_url=args.api_url)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 