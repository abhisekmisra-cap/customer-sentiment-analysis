"""
Test script to debug food classification
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

# Test comment
comment = "The pasta was undercooked and the service was slow. Very disappointed."

print(f"\nComment: {comment}")

# Test classification with debug output
result = analyzer.classification_chain.invoke({"comment": comment})
print(f"\nRaw classification output: '{result}'")
print(f"Output type: {type(result)}")

if hasattr(result, 'content'):
    print(f"Content: '{result.content}'")
    print(f"Content upper: '{result.content.strip().upper()}'")

category = analyzer.classify_comment(comment)
print(f"\nParsed category: {category}")

# Full analysis
full_result = analyzer.analyze_comment(comment)
print(f"\nFull analysis: {full_result}")
