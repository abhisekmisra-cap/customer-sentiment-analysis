"""
Test script to debug sentiment analysis
"""
import os
from customer_comment_analyzer import CustomerCommentAnalyzer

# Get token from environment
hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")

if not hf_token:
    print("ERROR: HUGGINGFACEHUB_API_TOKEN not set")
    exit(1)

print("Initializing analyzer...")
analyzer = CustomerCommentAnalyzer(hf_token=hf_token)

# Test comments
test_comments = [
    "The flight was terrible! Delayed for 5 hours with no explanation.",
    "Excellent hotel service! The staff was so friendly and helpful.",
    "The food was okay, nothing special but not bad either."
]

print("\nTesting sentiment analysis:")
print("=" * 80)

for comment in test_comments:
    print(f"\nComment: {comment}")
    
    # Test classification
    category = analyzer.classify_comment(comment)
    print(f"Category: {category}")
    
    # Test sentiment with debug output
    result = analyzer.sentiment_chain.invoke({"comment": comment})
    print(f"Raw model output: '{result}'")
    print(f"Output type: {type(result)}")
    print(f"Output repr: {repr(result)}")
    
    sentiment = analyzer.analyze_sentiment(comment)
    print(f"Parsed sentiment: {sentiment}")
    print("-" * 80)
