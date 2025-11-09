"""
Test script to verify all classifications work correctly
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

# Test comments for each category
test_cases = [
    {
        "comment": "The pasta was undercooked and the service was slow. Very disappointed.",
        "expected_category": "FOOD",
        "expected_sentiment": "NEGATIVE"
    },
    {
        "comment": "The flight was delayed for 3 hours with no explanation.",
        "expected_category": "TRAVEL",
        "expected_sentiment": "NEGATIVE"
    },
    {
        "comment": "The hotel room was spacious and clean. Great experience!",
        "expected_category": "ACCOMMODATION",
        "expected_sentiment": "POSITIVE"
    },
    {
        "comment": "The sushi was absolutely delicious and fresh.",
        "expected_category": "FOOD",
        "expected_sentiment": "POSITIVE"
    },
    {
        "comment": "The airline staff was friendly but the seats were uncomfortable.",
        "expected_category": "TRAVEL",
        "expected_sentiment": "NEUTRAL"
    }
]

print("\n" + "="*80)
print("TESTING CLASSIFICATION AND SENTIMENT ANALYSIS")
print("="*80)

correct_category = 0
correct_sentiment = 0
total = len(test_cases)

for i, test in enumerate(test_cases, 1):
    print(f"\n[Test {i}] {test['comment']}")
    
    result = analyzer.analyze_comment(test['comment'])
    
    category_match = "✓" if result['category'] == test['expected_category'] else "✗"
    sentiment_match = "✓" if result['sentiment'] == test['expected_sentiment'] else "✗"
    
    if result['category'] == test['expected_category']:
        correct_category += 1
    if result['sentiment'] == test['expected_sentiment']:
        correct_sentiment += 1
    
    print(f"  Expected: {test['expected_category']} / {test['expected_sentiment']}")
    print(f"  Got:      {result['category']} {category_match} / {result['sentiment']} {sentiment_match}")

print("\n" + "="*80)
print(f"RESULTS:")
print(f"  Category Accuracy:  {correct_category}/{total} ({correct_category/total*100:.1f}%)")
print(f"  Sentiment Accuracy: {correct_sentiment}/{total} ({correct_sentiment/total*100:.1f}%)")
print("="*80)
