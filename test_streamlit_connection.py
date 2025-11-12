"""
Test script to diagnose Streamlit MCP connection issues
"""
import os
import sys
from pathlib import Path

# Set Azure OpenAI credentials from environment variables
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/")
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY", "your-api-key-here")
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")

print("Testing MCP Client Connection...")
print(f"Endpoint: {os.environ['AZURE_OPENAI_ENDPOINT']}")
print(f"Deployment: {os.environ['AZURE_OPENAI_DEPLOYMENT_NAME']}")
print()

# Add mcp_integration directory to path
mcp_dir = Path(__file__).parent / "mcp_integration"
sys.path.insert(0, str(mcp_dir))

try:
    from mcp_client import SimpleMCPClient
    
    print("1. Creating MCP client...")
    server_path = Path(__file__).parent / "mcp_integration" / "mcp_server.py"
    client = SimpleMCPClient(server_script_path=str(server_path))
    
    print("2. Connecting to MCP server...")
    client.connect()
    print("✅ Connected successfully!")
    
    print("\n3. Testing comment analysis...")
    result = client.analyze_comment("The hotel room was dirty and uncomfortable")
    print(f"✅ Analysis result: {result}")
    
    print("\n4. Disconnecting...")
    client.disconnect()
    print("✅ Disconnected successfully!")
    
    print("\n🎉 All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
