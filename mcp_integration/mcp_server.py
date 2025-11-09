"""
MCP Server for Customer Comment Analysis
-----------------------------------------
Exposes comment analysis functionality through Model Context Protocol.
"""

import asyncio
import json
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from mcp.server.stdio import stdio_server
import sys
from pathlib import Path

# Add parent directory to path to import customer_comment_analyzer
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from customer_comment_analyzer import CustomerCommentAnalyzer
import os

# Initialize the MCP server
app = Server("customer-comment-analyzer")

# Global analyzer instance
analyzer: CustomerCommentAnalyzer | None = None


def get_analyzer() -> CustomerCommentAnalyzer:
    """Get or create the analyzer instance."""
    global analyzer
    if analyzer is None:
        hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        if not hf_token:
            raise ValueError(
                "HUGGINGFACEHUB_API_TOKEN environment variable is required. "
                "Get your token from https://huggingface.co/settings/tokens"
            )
        analyzer = CustomerCommentAnalyzer(hf_token=hf_token)
    return analyzer


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for comment analysis."""
    return [
        Tool(
            name="classify_comment",
            description="Classify a customer comment into one of three categories: TRAVEL, ACCOMMODATION, or FOOD. "
                       "This tool analyzes the content of the comment and determines which service category it relates to.",
            inputSchema={
                "type": "object",
                "properties": {
                    "comment": {
                        "type": "string",
                        "description": "The customer comment text to classify"
                    }
                },
                "required": ["comment"]
            }
        ),
        Tool(
            name="analyze_sentiment",
            description="Analyze the sentiment of a customer comment. "
                       "Determines whether the comment expresses POSITIVE, NEGATIVE, or NEUTRAL sentiment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "comment": {
                        "type": "string",
                        "description": "The customer comment text to analyze for sentiment"
                    }
                },
                "required": ["comment"]
            }
        ),
        Tool(
            name="analyze_comment",
            description="Perform complete analysis on a customer comment, including both category classification "
                       "and sentiment analysis. Returns comprehensive results with category (TRAVEL/ACCOMMODATION/FOOD) "
                       "and sentiment (POSITIVE/NEGATIVE/NEUTRAL).",
            inputSchema={
                "type": "object",
                "properties": {
                    "comment": {
                        "type": "string",
                        "description": "The customer comment text to analyze"
                    }
                },
                "required": ["comment"]
            }
        ),
        Tool(
            name="analyze_batch",
            description="Analyze multiple customer comments at once. Performs both classification and sentiment "
                       "analysis on each comment and returns results for all comments. Efficient for processing "
                       "multiple comments in a single request.",
            inputSchema={
                "type": "object",
                "properties": {
                    "comments": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Array of customer comment texts to analyze"
                    }
                },
                "required": ["comments"]
            }
        ),
        Tool(
            name="get_statistics",
            description="Calculate statistics from a list of analysis results. Provides category distribution "
                       "and sentiment distribution with counts and percentages. Useful for understanding "
                       "overall trends in customer feedback.",
            inputSchema={
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "comment": {"type": "string"},
                                "category": {"type": "string"},
                                "sentiment": {"type": "string"}
                            }
                        },
                        "description": "Array of analysis results with comment, category, and sentiment"
                    }
                },
                "required": ["results"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls from MCP clients."""
    
    try:
        analyzer = get_analyzer()
        
        if name == "classify_comment":
            comment = arguments.get("comment")
            if not comment:
                return [TextContent(type="text", text=json.dumps({"error": "Comment is required"}))]
            
            category = analyzer.classify_comment(comment)
            result = {
                "comment": comment,
                "category": category
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analyze_sentiment":
            comment = arguments.get("comment")
            if not comment:
                return [TextContent(type="text", text=json.dumps({"error": "Comment is required"}))]
            
            sentiment = analyzer.analyze_sentiment(comment)
            result = {
                "comment": comment,
                "sentiment": sentiment
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analyze_comment":
            comment = arguments.get("comment")
            if not comment:
                return [TextContent(type="text", text=json.dumps({"error": "Comment is required"}))]
            
            result = analyzer.analyze_comment(comment)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analyze_batch":
            comments = arguments.get("comments", [])
            if not comments:
                return [TextContent(type="text", text=json.dumps({"error": "Comments array is required"}))]
            
            results = analyzer.analyze_batch(comments)
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        
        elif name == "get_statistics":
            results = arguments.get("results", [])
            if not results:
                return [TextContent(type="text", text=json.dumps({"error": "Results array is required"}))]
            
            # Calculate statistics
            categories = {}
            sentiments = {}
            total = len(results)
            
            for result in results:
                cat = result.get('category', 'UNKNOWN')
                sent = result.get('sentiment', 'NEUTRAL')
                categories[cat] = categories.get(cat, 0) + 1
                sentiments[sent] = sentiments.get(sent, 0) + 1
            
            stats = {
                "total_comments": total,
                "category_distribution": {
                    cat: {
                        "count": count,
                        "percentage": round((count / total) * 100, 1)
                    }
                    for cat, count in categories.items()
                },
                "sentiment_distribution": {
                    sent: {
                        "count": count,
                        "percentage": round((count / total) * 100, 1)
                    }
                    for sent, count in sentiments.items()
                }
            }
            return [TextContent(type="text", text=json.dumps(stats, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    
    except Exception as e:
        error_result = {
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    print("Starting Customer Comment Analyzer MCP Server...")
    print("Make sure HUGGINGFACEHUB_API_TOKEN is set in environment variables.")
    asyncio.run(main())
