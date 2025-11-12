"""
Test the refactored CustomerCommentAnalyzer with tools using Azure OpenAI
"""
import os

# Set Azure OpenAI credentials from environment variables
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT", "https://openai-test28.openai.azure.com/")
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY", "your-api-key-here")
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")

from customer_comment_analyzer import CustomerCommentAnalyzer

def test_tools():
    print("Testing CustomerCommentAnalyzer with Azure OpenAI...")
    
    # Create analyzer with Azure OpenAI credentials
    print("\n1. Creating analyzer with Azure OpenAI...")
    analyzer = CustomerCommentAnalyzer(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
    )
    
    # Get tools
    print("\n2. Getting available tools...")
    tools = analyzer.get_tools()
    print(f"   Available tools: {[tool.name for tool in tools]}")
    
    # Test classification tool
    print("\n3. Testing classification tool directly...")
    comment = "The flight was delayed for 3 hours"
    category = analyzer.classify_comment(comment)
    print(f"   Comment: '{comment}'")
    print(f"   Category: {category}")
    
    # Test sentiment tool
    print("\n4. Testing sentiment tool directly...")
    sentiment = analyzer.analyze_sentiment(comment)
    print(f"   Sentiment: {sentiment}")
    
    # Test complete analysis
    print("\n5. Testing complete analysis (using tools)...")
    result = analyzer.analyze_comment(comment)
    print(f"   Result: {result}")
    
    # Test batch analysis
    print("\n6. Testing batch analysis...")
    comments = [
        "The hotel room was amazing and very clean!",
        "Food was terrible and overpriced",
        "Flight crew was professional"
    ]
    results = analyzer.analyze_batch(comments)
    for i, r in enumerate(results, 1):
        print(f"   {i}. {r['category']} / {r['sentiment']}: {r['comment'][:50]}...")
    
    print("\n✅ All tool tests passed!")

if __name__ == "__main__":
    test_tools()
