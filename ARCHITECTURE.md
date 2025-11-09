# Customer Comment Analyzer - Architecture Documentation

## System Architecture Overview

The Customer Comment Analyzer uses **Model Context Protocol (MCP)** architecture to separate the AI analysis logic from the user interface, providing better scalability, maintainability, and testability.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Customer Comment Analyzer                             │
│              AI-Powered Comment Classification System (MCP-Enabled)           │
└──────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    Streamlit Web Application                           │ │
│  │                           (app.py)                                     │ │
│  │                                                                        │ │
│  │  Features:                                                             │ │
│  │  • Single Comment Analysis                                             │ │
│  │  • Batch Analysis with Progress Tracking                              │ │
│  │  • Sample Comment Loading                                              │ │
│  │  • Visual Statistics Dashboard                                         │ │
│  │  • CSV Export Functionality                                            │ │
│  │  • Analysis History                                                    │ │
│  │  • Hugging Face Token Input                                            │ │
│  └────────────────────────────┬───────────────────────────────────────────┘ │
│                                │                                             │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 │
                                 │ Uses
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MCP CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                  SimpleMCPClient                                       │ │
│  │            (mcp_integration/mcp_client.py)                             │ │
│  │                                                                        │ │
│  │  • Synchronous MCP client using subprocess                            │ │
│  │  • JSON-RPC communication over stdin/stdout                           │ │
│  │  • Threading for non-blocking I/O                                     │ │
│  │  • Reliable error handling                                            │ │
│  │                                                                        │ │
│  │  Methods:                                                              │ │
│  │  ├─ connect()          - Start MCP server subprocess                  │ │
│  │  ├─ disconnect()       - Stop MCP server                              │ │
│  │  ├─ analyze_comment()  - Full analysis (category + sentiment)         │ │
│  │  ├─ classify_comment() - Category classification only                 │ │
│  │  ├─ analyze_sentiment()- Sentiment analysis only                      │ │
│  │  ├─ analyze_batch()    - Process multiple comments                    │ │
│  │  └─ get_statistics()   - Calculate result statistics                  │ │
│  └────────────────────────────┬───────────────────────────────────────────┘ │
│                                │                                             │
│                                │ JSON-RPC over stdio                         │
│                                │ (subprocess)                                │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MCP SERVER LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      MCP Server                                        │ │
│  │            (mcp_integration/mcp_server.py)                             │ │
│  │                                                                        │ │
│  │  Exposes AI analysis as MCP tools:                                     │ │
│  │                                                                        │ │
│  │  Tools:                                                                │ │
│  │  ├─ classify_comment   - Classify into TRAVEL/ACCOMMODATION/FOOD      │ │
│  │  ├─ analyze_sentiment  - Determine POSITIVE/NEGATIVE/NEUTRAL          │ │
│  │  ├─ analyze_comment    - Complete analysis                            │ │
│  │  ├─ analyze_batch      - Batch processing                             │ │
│  │  └─ get_statistics     - Statistical analysis                         │ │
│  │                                                                        │ │
│  │  Protocol: Model Context Protocol (JSON-RPC)                          │ │
│  └────────────────────────────┬───────────────────────────────────────────┘ │
│                                │                                             │
│                                │ Uses                                        │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CORE ANALYSIS LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │               CustomerCommentAnalyzer                                  │ │
│  │            (customer_comment_analyzer.py)                              │ │
│  │                                                                        │ │
│  │  Core business logic for AI-powered analysis                          │ │
│  │                                                                        │ │
│  │  Components:                                                           │ │
│  │  ├─ LangChain Integration                                             │ │
│  │  ├─ Prompt Template Loading                                           │ │
│  │  ├─ LLM Chain Execution                                               │ │
│  │  └─ Result Parsing & Validation                                       │ │
│  └────────────────────────────┬───────────────────────────────────────────┘ │
│                                │                                             │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 │
                                 │ Uses
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LANGCHAIN ORCHESTRATION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────┐    ┌──────────────────────────────┐      │
│  │   Classification Chain       │    │   Sentiment Analysis Chain   │      │
│  │                              │    │                              │      │
│  │  ┌────────────────────────┐  │    │  ┌────────────────────────┐  │     │
│  │  │   PromptTemplate       │  │    │  │   PromptTemplate       │  │     │
│  │  │                        │  │    │  │                        │  │     │
│  │  │   From: prompts/       │  │    │  │   From: prompts/       │  │     │
│  │  │   classification_      │  │    │  │   sentiment_           │  │     │
│  │  │   prompt.txt           │  │    │  │   prompt.txt           │  │     │
│  │  └───────────┬────────────┘  │    │  └───────────┬────────────┘  │     │
│  │              ▼               │    │              ▼               │     │
│  │  ┌────────────────────────┐  │    │  ┌────────────────────────┐  │     │
│  │  │      LLMChain          │  │    │  │      LLMChain          │  │     │
│  │  └───────────┬────────────┘  │    │  └───────────┬────────────┘  │     │
│  └──────────────┼───────────────┘    └──────────────┼───────────────┘     │
│                 │                                    │                      │
│                 └────────────────┬───────────────────┘                      │
│                                  ▼                                          │
│                    ┌──────────────────────────────┐                         │
│                    │   HuggingFaceEndpoint        │                         │
│                    │                              │                         │
│                    │   Configuration:             │                         │
│                    │   • Model: Llama 3.2         │                         │
│                    │   • Temperature: 0.3         │                         │
│                    │   • Max Tokens: 512          │                         │
│                    └──────────────┬───────────────┘                         │
│                                   │                                         │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
                                    │ HTTP API Request
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HUGGING FACE API                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    ┌──────────────────────────────┐                          │
│                    │    Meta Llama 3.2 Model      │                          │
│                    │                              │                          │
│                    │    Large Language Model      │                          │
│                    │    • Instruction-following   │                          │
│                    │    • Text generation         │                          │
│                    │    • Classification tasks    │                          │
│                    └──────────────────────────────┘                          │
│                                                                              │
│                    Authentication: HUGGINGFACEHUB_API_TOKEN                 │
│                    Rate Limiting: Based on tier                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW & PROCESSING                              │
└─────────────────────────────────────────────────────────────────────────────┘

   INPUT                    PROCESSING                      OUTPUT
┌──────────┐            ┌────────────────┐            ┌──────────────┐
│ Customer │            │ Classification │            │   Category   │
│ Comment  │───────────▶│     Chain      │───────────▶│   TRAVEL     │
│  Text    │            └────────────────┘            │ACCOMMODATION │
└──────────┘                    │                     │   FOOD       │
                                │                     └──────────────┘
                                │
                                ▼
                        ┌────────────────┐            ┌──────────────┐
                        │   Sentiment    │            │   Sentiment  │
                        │     Chain      │───────────▶│   POSITIVE   │
                        └────────────────┘            │   NEGATIVE   │
                                                      │   NEUTRAL    │
                                                      └──────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                          SUPPORTING COMPONENTS                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────────────┐          ┌────────────────────┐
│   Prompt Files     │          │   Sample Data      │
│   (prompts/)       │          │ (sample_comments.py)│
│                    │          │                    │
│   ├── classification          │   - Travel data    │
│   │   _prompt.txt  │          │   - Accommodation  │
│   ├── sentiment_   │          │   - Food data      │
│   │   prompt.txt   │          │   - Mixed data     │
│   └── README.md    │          └────────────────────┘
│                    │
│   Editable without │
│   code changes     │
└────────────────────┘
   └─────┬─────┘


## MCP Architecture Benefits

### Separation of Concerns
- **UI Layer**: Streamlit handles only presentation
- **Client Layer**: SimpleMCPClient manages communication
- **Server Layer**: MCP Server exposes tools
- **Logic Layer**: CustomerCommentAnalyzer contains business logic

### Scalability
- MCP server can be deployed independently
- Multiple clients can connect to one server
- Easy to scale horizontally

### Maintainability
- Clear boundaries between components
- Independent testing of each layer
- Easy to modify or replace components

### Reliability
- Subprocess-based communication (no async issues)
- JSON-RPC protocol for structured communication
- Proper error handling at each layer


## Key Design Decisions

### 1. Synchronous MCP Client (SimpleMCPClient)
**Decision**: Use subprocess with threading instead of async/await

**Rationale**:
- Streamlit has issues with asyncio event loops
- Subprocess approach is more reliable
- Threading handles I/O without blocking
- Simpler error handling and debugging

### 2. Prompt Template Externalization
**Decision**: Store prompts in separate `.txt` files

**Rationale**:
- Easy to modify prompts without code changes
- Version control for prompt engineering
- Better prompt management
- Supports A/B testing

### 3. MCP Protocol Implementation
**Decision**: Use Model Context Protocol for client-server communication

**Rationale**:
- Standardized protocol
- Tool-based architecture
- Better separation of concerns
- Industry best practice


## File Structure

```
Customer Sentiment Analysis/
├── app.py                          # Main Streamlit application (MCP-enabled)
├── customer_comment_analyzer.py    # Core analysis logic
├── sample_comments.py              # Sample data
├── requirements.txt                # Python dependencies
├── README.md                       # User documentation
├── ARCHITECTURE.md                 # This file
├── mcp_integration/                # MCP components
│   ├── mcp_client.py              # Synchronous MCP client
│   ├── mcp_server.py              # MCP server
│   ├── __init__.py                # Package marker
│   └── README.md                  # MCP documentation
└── prompts/                        # Prompt templates
    ├── classification_prompt.txt   # Category classification
    ├── sentiment_prompt.txt        # Sentiment analysis
    └── README.md                   # Prompt documentation
```


## Data Flow Example

### Single Comment Analysis

1. **User Input**: "The flight was comfortable but delayed"
2. **Streamlit UI**: Captures input, sends to MCP client
3. **MCP Client**: Calls `analyze_comment()` tool via JSON-RPC
4. **MCP Server**: Receives request, forwards to analyzer
5. **Analyzer**: 
   - Loads classification prompt
   - Calls LLM for category → "TRAVEL"
   - Loads sentiment prompt
   - Calls LLM for sentiment → "NEUTRAL"
6. **Response**: Flows back through layers
7. **Display**: Results shown in Streamlit UI


## Technology Stack

- **Frontend**: Streamlit 1.28+
- **AI/ML**: LangChain, Hugging Face Transformers
- **LLM**: Meta Llama 3.2 (via Hugging Face API)
- **Protocol**: Model Context Protocol (MCP) 0.9+
- **Language**: Python 3.8+
- **Communication**: JSON-RPC over stdio


## Future Enhancements

- [ ] Add more categories (entertainment, shopping, etc.)
- [ ] Support for multiple languages
- [ ] Confidence scores for predictions
- [ ] Model fine-tuning capabilities
- [ ] RESTful API wrapper
- [ ] WebSocket support for real-time analysis
- [ ] Caching layer for improved performance
- [ ] Database integration for persistent storage


┌───────────────────────────────────────────────────────────────────────────────┐
│                          SECURITY & CONFIGURATION                              │
└───────────────────────────────────────────────────────────────────────────────┘

Environment Variables:
┌──────────────────────────────────────┐
│ HUGGINGFACEHUB_API_TOKEN             │
│ ↳ Required for API authentication    │
│ ↳ Get from: huggingface.co/settings │
└──────────────────────────────────────┘

Configuration Files:
┌──────────────────────────────────────┐
│ requirements.txt                     │
│ ↳ All Python dependencies           │
│                                      │
│ prompts/*.txt                        │
│ ↳ Editable prompt templates         │
└──────────────────────────────────────┘


┌───────────────────────────────────────────────────────────────────────────────┐
│                          TECHNOLOGY STACK                                      │
└───────────────────────────────────────────────────────────────────────────────┘

┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│  Frontend   │  Backend    │  AI/ML      │  Protocol   │  Data       │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Streamlit   │ Python 3.13 │ LangChain   │ MCP         │ Pandas      │
│             │             │ Transformers│ JSON-RPC    │ CSV         │
│             │             │ PyTorch     │ stdio       │             │
│             │             │ Hugging Face│             │             │
│             │             │ Mistral-7B  │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘


┌───────────────────────────────────────────────────────────────────────────────┐
│                          SCALABILITY & EXTENSIBILITY                           │
└───────────────────────────────────────────────────────────────────────────────┘

Horizontal Scaling (MCP):
┌────────────┐  ┌────────────┐  ┌────────────┐
│  Client 1  │  │  Client 2  │  │  Client 3  │
│ (Streamlit)│  │   (CLI)    │  │  (Mobile)  │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │
      └───────────────┼───────────────┘
                      │
                ┌─────▼─────┐
                │    MCP    │
                │  Server   │
                └─────┬─────┘
                      │
                ┌─────▼─────┐
                │ AI Engine │
                └───────────┘

Extensibility:
• Add new categories by editing prompts/classification_prompt.txt
• Add new sentiments by editing prompts/sentiment_prompt.txt
• Add new tools in mcp/mcp_server.py
• Switch models by changing repo_id in analyzer
• Add new UI by implementing MCP client


┌───────────────────────────────────────────────────────────────────────────────┐
│                          PERFORMANCE CHARACTERISTICS                           │
└───────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────┐
│ First-time Initialization          │
│ ├─ Model Loading: 30-60 seconds    │
│ └─ Connection: 5-10 seconds        │
│                                    │
│ Subsequent Requests                │
│ ├─ Single Analysis: 2-5 seconds    │
│ └─ Batch (10 items): 10-30 seconds │
│                                    │
│ Memory Usage                       │
│ ├─ Base: ~500MB                    │
│ └─ With Model: ~2-3GB              │
└────────────────────────────────────┘
