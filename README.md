# Customer Comment Analyzer 🤖

An intelligent Python application that uses **LangChain**, **Hugging Face LLMs**, and **Model Context Protocol (MCP)** to automatically classify customer comments into categories (Travel, Accommodation, Food) and analyze their sentiment (Positive, Negative, Neutral).

## Features ✨

### Core Features
- **Category Classification**: Automatically categorizes customer comments into:
  - ✈️ Travel (flights, airlines, transportation)
  - 🏨 Accommodation (hotels, lodging, stays)
  - 🍽️ Food (restaurants, dining, meals)

- **Sentiment Analysis**: Determines if comments are:
  - 😊 Positive
  - 😞 Negative
  - 😐 Neutral

- **Batch Processing**: Analyze multiple comments at once with progress tracking
- **Statistics Dashboard**: Interactive charts showing category and sentiment distribution
- **Export Functionality**: Download analysis results as CSV files
- **Analysis History**: Track all previous analyses with timestamps

### Technical Features
- **Model Context Protocol (MCP)**: Server-client architecture for production deployment
- **External Prompt Templates**: Easily customizable prompts stored in separate files
- **Web Interface**: Streamlit app with MCP integration
- **Powered by AI**: Uses Meta Llama 3.2 model via Hugging Face
- **Synchronous MCP Client**: Reliable subprocess-based communication

## Architecture 🏗️

The application uses **Model Context Protocol (MCP)** architecture:

```
┌─────────────────┐         MCP Protocol        ┌──────────────────┐
│                 │◄────────────────────────────►│                  │
│  Streamlit App  │    JSON-RPC over stdio       │   MCP Server     │
│    (app.py)     │                              │  (mcp_server.py) │
└─────────────────┘                              └──────────────────┘
        │                                                 │
        │                                                 ▼
        │                                         ┌──────────────────┐
        │                                         │  LangChain +     │
        └─────────────────────────────────────────│  Hugging Face    │
                  via mcp_client.py               │  Analysis Logic  │
                                                  └──────────────────┘
```

See `ARCHITECTURE.md` for detailed architecture documentation.

## Prerequisites 📋

- Python 3.8 or higher
- Hugging Face account and API token ([Get one here](https://huggingface.co/settings/tokens))
- Internet connection for API calls

## Installation 🚀

1. **Clone or navigate to the project directory**:
   ```powershell
   cd "c:\Abhishek\Purdue-Python\Customer Sentiment Analysis"
   ```

2. **Install required packages**:
   ```powershell
   pip install -r requirements.txt
   ```
   
   This installs all dependencies including:
   - LangChain and Hugging Face integration
   - Streamlit for web interface
   - Model Context Protocol (MCP) for service architecture
   - All required AI/ML libraries

3. **Set up your Hugging Face API token**:
   
   Get your token from: https://huggingface.co/settings/tokens
   
   **Option A**: Set as environment variable (recommended):
   ```powershell
   $env:HUGGINGFACEHUB_API_TOKEN='your_token_here'
   ```
   
   **Option B**: Enter token in the web interface when prompted

## Usage 💻

### Web Application (Recommended) 🌐

Launch the MCP-enabled Streamlit web interface:

```powershell
streamlit run app.py
```

The application will automatically:
- Start the MCP server in the background
- Connect the client to the server
- Initialize the AI model

The web interface provides:
- **Token Input**: Enter your Hugging Face token to connect
- **Single Comment Analysis**: Analyze one comment at a time
- **Batch Analysis**: Process multiple comments together
- **Load Sample Data**: Pre-loaded examples for each category
- **Visual Statistics**: Charts and graphs of results
- **Export Results**: Download analysis as CSV
- **Analysis History**: Track all your previous analyses

### Command Line Usage

**Run the standalone analyzer:**
```powershell
C:/Python313/python.exe customer_comment_analyzer.py
```

**Test the MCP server:**
```powershell
C:/Python313/python.exe mcp/mcp_server.py
```

**Test the MCP client:**
```powershell
C:/Python313/python.exe mcp/mcp_client.py
```

**View sample comments:**
```powershell
C:/Python313/python.exe sample_comments.py
```

### Programmatic Usage

**Using the analyzer directly:**
```python
from customer_comment_analyzer import CustomerCommentAnalyzer

# Initialize the analyzer
analyzer = CustomerCommentAnalyzer(hf_token="your_token_here")

# Analyze a single comment
result = analyzer.analyze_comment("The flight was delayed but staff was helpful")
print(result)
# Output: {'comment': '...', 'category': 'AIRLINE', 'sentiment': 'NEUTRAL'}

# Analyze multiple comments
comments = [
    "Hotel room was amazing!",
    "Food was terrible",
    "Flight delayed again"
]
results = analyzer.analyze_batch(comments)
analyzer.print_results(results)
```

**Using the MCP client:**
```python
# Add mcp directory to path if needed
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "mcp"))

from mcp.mcp_client import SyncCommentAnalyzerClient

# Using context manager (recommended)
with SyncCommentAnalyzerClient() as client:
    result = client.analyze_comment("Great service!")
    print(result)
    
    # Batch analysis
    results = client.analyze_batch(["Comment 1", "Comment 2"])
    
    # Get statistics
    stats = client.get_statistics(results)
    print(stats)
```

**Using sample comments:**
```python
from sample_comments import get_comments_by_category

# Get specific category comments
airline_comments = get_comments_by_category('airline')
hotel_comments = get_comments_by_category('hotel')
food_comments = get_comments_by_category('food')
mixed_comments = get_comments_by_category('mixed')
all_comments = get_comments_by_category('all')
```

## Project Structure 📁

```
Langchain/
│
├── mcp/                            # Model Context Protocol implementation
│   ├── mcp_server.py               # MCP server exposing AI tools
│   ├── mcp_client.py               # MCP client library
│   ├── app_mcp.py                  # Streamlit app using MCP
│   └── README.md                   # MCP architecture documentation
│
├── prompts/                        # Prompt template files
│   ├── classification_prompt.txt   # Category classification template
│   ├── sentiment_prompt.txt        # Sentiment analysis template
│   └── README.md                   # Prompt customization guide
│
├── app.py                          # Streamlit web app (direct integration)
├── customer_comment_analyzer.py    # Core AI analysis logic
├── sample_comments.py              # Sample customer comments
├── example_usage.py                # Usage examples
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## How It Works 🔧

1. **LangChain Integration**: Uses LangChain's `HuggingFaceEndpoint` to connect to Hugging Face models
2. **External Prompt Templates**: Prompts are stored in separate text files for easy customization
3. **Model Context Protocol**: Optional MCP architecture for service-based deployment
4. **Chain Architecture**: Separate chains for classification and sentiment analysis
5. **Model**: Uses Mistral-7B-Instruct-v0.2, a powerful instruction-following model

### Architecture Options

**Direct Integration** (`app.py`):
- Simple, single-process design
- Direct function calls to analyzer
- Good for development and prototyping

**MCP Architecture** (`mcp/app_mcp.py` + `mcp/mcp_server.py`):
- Client-server architecture
- Standardized protocol communication
- Better for production deployment
- Independent scaling of UI and AI
- Multiple client support
- See `mcp/README.md` for complete details

### Prompt Templates

All prompt templates are externalized to the `prompts/` directory for easy modification without code changes:

**Available Templates:**
- **`classification_prompt.txt`** - Category classification instructions
- **`sentiment_prompt.txt`** - Sentiment analysis instructions
- **`README.md`** - Complete customization guide with examples

**Benefits:**
- Edit prompts without touching code
- Version control for prompt changes
- Easy A/B testing of different prompts
- No redeployment needed for prompt updates

**Example template structure:**
```text
Classify the following customer comment into ONE of these categories: 
AIRLINE, HOTEL, or FOOD.
Only respond with one of these three words in uppercase.

Customer comment: {comment}

Category:
```

See `prompts/README.md` for detailed customization examples including:
- Adding new categories
- Implementing few-shot learning
- Changing sentiment granularity
- Custom output formats

## Example Output 📊

**Command Line Output:**
```
================================================================================
CUSTOMER COMMENT ANALYSIS RESULTS
================================================================================

--- Comment 1 ---
Text: The flight was delayed by 3 hours and the staff was very rude.
Category: AIRLINE
Sentiment: NEGATIVE

--- Comment 2 ---
Text: Hotel room was clean and spacious. The breakfast buffet was amazing!
Category: HOTEL
Sentiment: POSITIVE

--- Comment 3 ---
Text: The pasta was undercooked and the service was slow.
Category: FOOD
Sentiment: NEGATIVE

================================================================================

SUMMARY STATISTICS
--------------------------------------------------------------------------------

Category Distribution:
  AIRLINE: 3 (33.3%)
  FOOD: 3 (33.3%)
  HOTEL: 3 (33.3%)

Sentiment Distribution:
  NEGATIVE: 4 (44.4%)
  NEUTRAL: 2 (22.2%)
  POSITIVE: 3 (33.3%)
================================================================================
```

## Customization 🎨

### Customizing Prompt Templates

Edit the template files in the `prompts/` directory to modify behavior:

**Example: Add more categories** (`prompts/classification_prompt.txt`):
```
Classify the following customer comment into ONE of these categories: 
AIRLINE, HOTEL, FOOD, CAR_RENTAL, or TOUR_PACKAGE.

Customer comment: {comment}

Category:
```

**Example: Add sentiment granularity** (`prompts/sentiment_prompt.txt`):
```
Analyze the sentiment of the following customer comment.
Classify it as: VERY_POSITIVE, POSITIVE, NEUTRAL, NEGATIVE, or VERY_NEGATIVE.

Customer comment: {comment}

Sentiment:
```

See `prompts/README.md` for more customization examples and best practices.

### Using Different Models

You can change the Hugging Face model by modifying the `repo_id` in `CustomerCommentAnalyzer.__init__()`:

```python
self.llm = HuggingFaceEndpoint(
    repo_id="google/flan-t5-large",  # Change to any compatible model
    temperature=0.3,
    max_new_tokens=512
)
```

Popular alternatives:
- `google/flan-t5-large` - Smaller, faster
- `HuggingFaceH4/zephyr-7b-beta` - Good for instructions
- `tiiuae/falcon-7b-instruct` - Efficient alternative

### Using Custom Prompts Directory

You can specify a custom location for prompt templates:

```python
analyzer = CustomerCommentAnalyzer(
    hf_token="your_token",
    prompts_dir="path/to/custom/prompts"
)
```

## Troubleshooting 🔍

### Common Issues

**"No Hugging Face token found"**
- Set your API token: `$env:HUGGINGFACEHUB_API_TOKEN='your_token_here'`
- Or enter it in the Streamlit sidebar
- Get token from: https://huggingface.co/settings/tokens

**Model loading is slow**
- First-time loading takes a few minutes (downloading model)
- Subsequent runs are much faster
- Consider using a smaller model for faster loading

**"Rate limit exceeded"**
- Free tier has request limits
- Wait a few minutes between large batches
- Upgrade to Hugging Face Pro for higher limits
- Consider local model inference for production

**MCP connection errors**
- Ensure environment variable is set before starting app
- Check that MCP files are in the `mcp/` directory
- Verify Python can import from the mcp directory
- Try the direct version (`app.py`) if MCP issues persist
- Check console output for detailed error messages

**"Prompt template file not found"**
- Ensure `prompts/` directory exists
- Check that `.txt` files are present
- Verify file paths are correct

**Token length errors**
- Reduce `max_new_tokens` parameter in `customer_comment_analyzer.py`
- Use shorter comments
- Try a different model with larger context window

### Performance Tips

- Use batch analysis for multiple comments (more efficient)
- Cache results to avoid re-analyzing same comments
- Consider running MCP server separately for better performance
- Use GPU if available (requires CUDA setup)

## API Rate Limits ⚠️

The free Hugging Face API has rate limits:
- Be mindful of the number of requests
- Consider using local model inference for large-scale applications
- Upgrade to Hugging Face Pro for higher limits

## Future Enhancements 🚀

Potential improvements and features:

- [ ] **Local Model Support** - Run models locally without API calls
- [ ] **Additional Export Formats** - JSON, Excel, PDF reports
- [ ] **Multi-language Support** - Analyze comments in multiple languages
- [ ] **Custom Categories** - User-defined classification categories
- [ ] **Advanced Analytics** - Word clouds, trend analysis, key phrase extraction
- [ ] **Real-time Processing** - WebSocket support for live comment streams
- [ ] **Database Integration** - Store results in PostgreSQL/MongoDB
- [ ] **REST API** - HTTP API endpoint for external integrations
- [ ] **Authentication** - User accounts and API key management
- [ ] **Fine-tuning** - Custom model training on domain-specific data
- [ ] **Confidence Scores** - Probability scores for predictions
- [ ] **A/B Testing** - Compare different prompts and models
- [ ] **Docker Support** - Containerized deployment
- [ ] **Cloud Deployment** - AWS/Azure/GCP deployment guides

## Technologies Used 🛠️

### Core Technologies
- **Python 3.13** - Programming language
- **LangChain** - LLM orchestration and chain management
- **Hugging Face Transformers** - AI model access and management
- **Mistral-7B-Instruct-v0.2** - Instruction-following language model

### Web & UI
- **Streamlit** - Interactive web application framework
- **Pandas** - Data manipulation and CSV export

### Model Context Protocol
- **MCP SDK** - Model Context Protocol implementation
- **httpx** - HTTP client for async operations
- **Pydantic** - Data validation

### AI/ML Libraries
- **torch (PyTorch)** - Deep learning framework
- **sentencepiece** - Tokenization
- **accelerate** - Model optimization
- **huggingface-hub** - Model repository access

## Quick Start Guide 🚀

### 1. Get Your Hugging Face Token
Visit https://huggingface.co/settings/tokens and create a free token

### 2. Set Environment Variable
```powershell
$env:HUGGINGFACEHUB_API_TOKEN='your_token_here'
```

### 3. Choose Your Interface

**Web Interface (Easiest):**
```powershell
C:/Python313/python.exe -m streamlit run app.py
```

**MCP Version (Production):**
```powershell
C:/Python313/python.exe -m streamlit run mcp/app_mcp.py
```

**Command Line:**
```powershell
C:/Python313/python.exe customer_comment_analyzer.py
```

### 4. Start Analyzing!
- Enter comments in the web interface, or
- Use the Python API in your own scripts

## Documentation 📚

- **README.md** (this file) - Main documentation and setup guide
- **mcp/README.md** - Model Context Protocol architecture details
- **prompts/README.md** - Prompt template customization guide
- Code comments - Inline documentation in all Python files

## Project Features Summary

| Feature | Direct Version | MCP Version |
|---------|---------------|-------------|
| Web Interface | ✅ `app.py` | ✅ `mcp/app_mcp.py` |
| Single Comment Analysis | ✅ | ✅ |
| Batch Processing | ✅ | ✅ |
| Statistics Dashboard | ✅ | ✅ |
| CSV Export | ✅ | ✅ |
| Analysis History | ✅ | ✅ |
| External Prompts | ✅ | ✅ |
| Client-Server Architecture | ❌ | ✅ |
| Independent Scaling | ❌ | ✅ |
| Multiple Clients | ❌ | ✅ |
| Production Ready | Good | Better |

## License 📄

This project is created for educational purposes.

## Contributing 🤝

Contributions are welcome! Here's how you can help:

1. **Report Bugs** - Open an issue with details
2. **Suggest Features** - Share your ideas for improvements
3. **Improve Documentation** - Help make docs clearer
4. **Submit PRs** - Fix bugs or add features
5. **Share Feedback** - Let us know how you're using it

## Support 💬

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review **mcp/README.md** for MCP-specific issues
3. Check **prompts/README.md** for prompt customization
4. Review [LangChain documentation](https://python.langchain.com/)
5. Visit [Hugging Face docs](https://huggingface.co/docs)
6. Check [Model Context Protocol docs](https://modelcontextprotocol.io/)

## Acknowledgments 🙏

Built with amazing open-source technologies:
- LangChain team for the excellent orchestration framework
- Hugging Face for democratizing AI model access
- Mistral AI for the powerful instruction-following model
- Streamlit for the intuitive web framework
- Model Context Protocol team for standardization

---

**Made with ❤️ using LangChain, Hugging Face, Model Context Protocol, and Streamlit**

*Happy Analyzing! 🎉*
