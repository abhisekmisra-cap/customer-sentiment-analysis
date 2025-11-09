"""
Simple MCP Client for Customer Comment Analysis
------------------------------------------------
Uses subprocess and JSON-RPC for communication, avoiding asyncio issues.
"""

import json
import subprocess
import sys
from typing import List, Dict, Optional
from pathlib import Path
import threading
import queue
import time


class SimpleMCPClient:
    """
    Simple synchronous MCP Client using subprocess.
    Works reliably in Streamlit without asyncio complications.
    """
    
    def __init__(self, server_script_path: str = None):
        """
        Initialize the simple MCP client.
        
        Args:
            server_script_path: Path to the MCP server script
        """
        if server_script_path is None:
            self.server_script_path = str(Path(__file__).parent / "mcp_server.py")
        else:
            self.server_script_path = server_script_path
        
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self._stdout_queue = queue.Queue()
        self._reader_thread = None
        self._stderr_thread = None
        self._running = False
    
    def connect(self):
        """Start the MCP server process."""
        if self.process is not None:
            return  # Already connected
        
        # Start the server process
        self.process = subprocess.Popen(
            [sys.executable, self.server_script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Start reader threads
        self._running = True
        self._reader_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader_thread.start()
        
        self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self._stderr_thread.start()
        
        # Initialize the session
        self._send_request("initialize", {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {
                "name": "customer-comment-analyzer-client",
                "version": "1.0.0"
            }
        })
        
        # Wait for initialization response
        response = self._get_response(timeout=30)
        if not response or "error" in response:
            raise RuntimeError(f"Failed to initialize MCP server: {response}")
    
    def disconnect(self):
        """Stop the MCP server process."""
        self._running = False
        
        if self.process:
            try:
                self.process.stdin.close()
                self.process.stdout.close()
                self.process.stderr.close()
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            finally:
                self.process = None
    
    def _read_stdout(self):
        """Read stdout in a background thread."""
        while self._running and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                self._stdout_queue.put(line)
            except:
                break
    
    def _read_stderr(self):
        """Read stderr in a background thread and print errors."""
        while self._running and self.process:
            try:
                line = self.process.stderr.readline()
                if not line:
                    break
                # Print stderr to console for debugging
                print(f"[MCP Server Error] {line.strip()}", file=sys.stderr)
            except:
                break
    
    def _send_request(self, method: str, params: dict = None) -> int:
        """Send a JSON-RPC request to the server."""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Not connected to MCP server")
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
        
        return self.request_id
    
    def _get_response(self, timeout: float = 30) -> dict:
        """Wait for and parse a response from the server."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                line = self._stdout_queue.get(timeout=0.1)
                if line.strip():
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
            except queue.Empty:
                continue
        
        raise TimeoutError("Timeout waiting for response from MCP server")
    
    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call a tool on the MCP server."""
        self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        response = self._get_response()
        
        if "error" in response:
            raise RuntimeError(f"Tool call failed: {response['error']}")
        
        # Extract the result from the response
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"]
            if content and len(content) > 0:
                text = content[0].get("text", "{}")
                return json.loads(text)
        
        return {}
    
    def analyze_comment(self, comment: str) -> Dict[str, str]:
        """
        Analyze a comment (classification + sentiment).
        
        Args:
            comment: The comment text
            
        Returns:
            Dict with 'comment', 'category', and 'sentiment'
        """
        return self.call_tool("analyze_comment", {"comment": comment})
    
    def classify_comment(self, comment: str) -> str:
        """
        Classify a customer comment.
        
        Args:
            comment: The comment text
            
        Returns:
            Category classification
        """
        result = self.call_tool("classify_comment", {"comment": comment})
        return result.get("category", "UNKNOWN")
    
    def analyze_sentiment(self, comment: str) -> str:
        """
        Analyze sentiment of a customer comment.
        
        Args:
            comment: The comment text
            
        Returns:
            Sentiment classification
        """
        result = self.call_tool("analyze_sentiment", {"comment": comment})
        return result.get("sentiment", "NEUTRAL")
    
    def analyze_batch(self, comments: List[str]) -> List[Dict[str, str]]:
        """
        Analyze multiple comments.
        
        Args:
            comments: List of comment texts
            
        Returns:
            List of analysis results
        """
        return self.call_tool("analyze_batch", {"comments": comments})
    
    def get_statistics(self, results: List[Dict[str, str]]) -> Dict:
        """
        Calculate statistics from analysis results.
        
        Args:
            results: List of analysis results
            
        Returns:
            Statistics dictionary
        """
        return self.call_tool("get_statistics", {"results": results})
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
