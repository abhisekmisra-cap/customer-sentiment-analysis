# Model Context Protocol (MCP) Integration

This directory contains the MCP server and client implementations for the Customer Comment Analyzer.

## Overview

The Model Context Protocol (MCP) provides a standardized way to expose AI capabilities as services. This implementation separates the AI analysis logic (server) from the user interface (client), providing:

- **Loose Coupling**: UI and AI logic are independent
- **Scalability**: Multiple clients can connect to one server
- **Standardization**: Uses MCP protocol for interoperability
- **Flexibility**: Easy to swap implementations

## Architecture

```
┌─────────────────┐         MCP Protocol        ┌──────────────────┐
│                 │◄────────────────────────────►│                  │
│  Streamlit App  │      JSON-RPC over stdio     │   MCP Server     │
│   (app_mcp.py)  │                              │  (mcp_server.py) │
│   in mcp/       │                              │   in mcp/        │
└─────────────────┘                              └──────────────────┘
        ▲                                                 │
        │                                                 │
        │                                                 ▼
        │                                         ┌──────────────────┐
        │                                         │  LangChain +     │
        └─────────────────────────────────────────│  Hugging Face    │
                  via mcp_client.py               │  Analysis Logic  │
                      in mcp/                     │  (in parent dir) │
                                                  └──────────────────┘
```

## Files

### `mcp_server.py`
The MCP server that exposes analysis functionality as tools:

**Available Tools:**
- `classify_comment` - Classify into AIRLINE/HOTEL/FOOD
- `analyze_sentiment` - Determine POSITIVE/NEGATIVE/NEUTRAL
- `analyze_comment` - Complete analysis (classification + sentiment)
- `analyze_batch` - Analyze multiple comments at once
- `get_statistics` - Calculate distribution statistics

**Running the server standalone:**
```powershell
$env:HUGGINGFACEHUB_API_TOKEN='your_token_here'
C:/Python313/python.exe mcp/mcp_server.py
```

### `mcp_client.py`
Client library for connecting to the MCP server:

**Two client variants:**
1. **`CommentAnalyzerMCPClient`** - Async client for async applications
2. **`SyncCommentAnalyzerClient`** - Synchronous wrapper for Streamlit

**Example usage:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "mcp"))

from mcp_client import SyncCommentAnalyzerClient

# Using context manager
with SyncCommentAnalyzerClient() as client:
    result = client.analyze_comment("Great flight!")
    print(result)  # {'comment': '...', 'category': 'AIRLINE', 'sentiment': 'POSITIVE'}
```

### `app_mcp.py`
Streamlit web application using MCP client:

**Features:**
- Connect/disconnect from MCP server
- Single comment analysis
- Batch comment analysis
- Real-time statistics via MCP
- Export results to CSV

**Running the app:**
```powershell
$env:HUGGINGFACEHUB_API_TOKEN='your_token_here'
C:/Python313/python.exe -m streamlit run mcp/app_mcp.py
```

## Protocol Details

### Communication Flow

1. **Client connects** to server via stdio (standard input/output)
2. **Client initializes** session with handshake
3. **Client calls tools** with JSON arguments
4. **Server processes** requests and returns JSON responses
5. **Client disconnects** when done

### Tool Call Format

**Request:**
```json
{
  "tool": "analyze_comment",
  "arguments": {
    "comment": "The hotel was wonderful!"
  }
}
```

**Response:**
```json
{
  "comment": "The hotel was wonderful!",
  "category": "HOTEL",
  "sentiment": "POSITIVE"
}
```

## Benefits of MCP Architecture

### 1. **Separation of Concerns**
- UI logic in Streamlit app
- AI logic in MCP server
- Clear boundaries and responsibilities

### 2. **Reusability**
- Same server can be used by multiple clients
- Web app, CLI, API, mobile app can all use same server

### 3. **Independent Scaling**
- Scale UI and AI independently
- Run multiple servers for load balancing
- Cache results at server level

### 4. **Testing**
- Test server independently of UI
- Mock server for UI testing
- Easy integration testing

### 5. **Deployment Flexibility**
- Server and client can run on different machines
- Containerize separately
- Deploy to different environments

## Development Tips

### Testing the Server
```powershell
# Start server in one terminal (from project root)
C:/Python313/python.exe mcp/mcp_server.py

# Test with client in another terminal (from project root)
C:/Python313/python.exe mcp/mcp_client.py
```

### Debugging
- Server logs to stdout/stderr
- Add print statements in `mcp/mcp_server.py` for debugging
- Check client connection errors in Streamlit UI
- Verify paths are correct when importing modules

### Adding New Tools

1. **Add tool definition** in `mcp/mcp_server.py`:
```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="my_new_tool",
            description="Description of what it does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter"}
                },
                "required": ["param"]
            }
        )
    ]
```

2. **Implement tool handler** in `mcp/mcp_server.py`:
```python
@app.call_tool()
async def call_tool(name: str, arguments: Any):
    if name == "my_new_tool":
        param = arguments.get("param")
        result = # ... process ...
        return [TextContent(type="text", text=json.dumps(result))]
```

3. **Add client method** in `mcp/mcp_client.py`:
```python
async def my_new_tool(self, param: str):
    result = await self.session.call_tool(
        "my_new_tool",
        arguments={"param": param}
    )
    return json.loads(result.content[0].text)
```

## Comparison: Direct vs MCP

### Direct Integration (`app.py`)
- Simple, fewer moving parts
- Direct function calls
- Single process
- Good for prototypes

### MCP Integration (`app_mcp.py`)
- More complex setup
- Network/IPC communication
- Separate processes
- Better for production

## Troubleshooting

### "Client not connected" error
Make sure to call `connect()` before using the client:
```python
client = SyncCommentAnalyzerClient()
client.connect()
# ... use client ...
client.disconnect()
```

### "HUGGINGFACEHUB_API_TOKEN not found"
Set the environment variable before starting:
```powershell
$env:HUGGINGFACEHUB_API_TOKEN='your_token_here'
```

### Server not responding
- Check if server process is running
- Verify token is set correctly
- Look for error messages in console

## Future Enhancements

- [ ] Add authentication/authorization
- [ ] Implement caching for repeated queries
- [ ] Add rate limiting
- [ ] Support HTTP/WebSocket transport
- [ ] Add metrics and monitoring
- [ ] Implement batch optimization
- [ ] Add request queuing

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [LangChain Documentation](https://python.langchain.com/)
