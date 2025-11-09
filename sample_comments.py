"""
Sample Customer Comments
-------------------------
A collection of sample customer comments for testing the analyzer.
"""

# Sample comments categorized by type
TRAVEL_COMMENTS = [
    "The flight was delayed by 3 hours and the staff was very rude. Worst experience ever!",
    "Great airline! The seats were comfortable and the crew was friendly.",
    "Smooth flight with on-time departure and arrival. Impressed!",
    "Lost my luggage and customer service was unhelpful. Very frustrating.",
    "The in-flight entertainment system wasn't working. Disappointing.",
    "Excellent service! The cabin crew went above and beyond.",
    "Seat was too cramped and no legroom at all. Uncomfortable journey.",
    "Check-in process was quick and efficient. Great experience!",
    "Flight was overbooked and I was bumped to a later flight. Terrible!",
    "Love the complimentary snacks and beverages. Will fly again!"
]

ACCOMMODATION_COMMENTS = [
    "Hotel room was clean and spacious. The breakfast buffet was amazing!",
    "The hotel location is perfect, right in the city center. Would definitely stay again!",
    "Room service was excellent but the bed was uncomfortable.",
    "Noisy neighbors kept me up all night. Poor soundproofing.",
    "Beautiful hotel with stunning views. Staff was courteous and helpful.",
    "The room was not cleaned properly and had a bad smell.",
    "Amazing amenities! The pool and gym were top-notch.",
    "Check-in took forever and the receptionist was unfriendly.",
    "Cozy rooms and great value for money. Highly recommend!",
    "WiFi didn't work in my room. Very inconvenient for business travel."
]

FOOD_COMMENTS = [
    "The pasta was undercooked and the service was slow. Very disappointed.",
    "Food arrived cold and tasted bland. Not worth the price.",
    "The restaurant ambiance is nice but the portions are too small.",
    "Absolutely delicious! Best Italian food I've had in years.",
    "Fresh ingredients and wonderful presentation. Chef's kiss!",
    "Waited 45 minutes for our order. Unacceptable service.",
    "The dessert was heavenly! Will come back for sure.",
    "Food was too salty and overpriced for what you get.",
    "Great vegetarian options and friendly staff. Loved it!",
    "The sushi was not fresh. Got a stomach ache afterwards."
]

# Mixed comments for general testing
MIXED_COMMENTS = [
    "The flight was delayed by 3 hours and the staff was very rude. Worst experience ever!",
    "Hotel room was clean and spacious. The breakfast buffet was amazing!",
    "The pasta was undercooked and the service was slow. Very disappointed.",
    "Great airline! The seats were comfortable and the crew was friendly.",
    "The hotel location is perfect, right in the city center. Would definitely stay again!",
    "Food arrived cold and tasted bland. Not worth the price.",
    "Smooth flight with on-time departure and arrival. Impressed!",
    "Room service was excellent but the bed was uncomfortable.",
    "The restaurant ambiance is nice but the portions are too small.",
    "Lost my luggage and customer service was unhelpful. Very frustrating.",
    "Beautiful hotel with stunning views. Staff was courteous and helpful.",
    "Absolutely delicious! Best Italian food I've had in years.",
    "Flight was overbooked and I was bumped to a later flight. Terrible!",
    "The room was not cleaned properly and had a bad smell.",
    "Fresh ingredients and wonderful presentation. Chef's kiss!",
]

# All comments combined
ALL_COMMENTS = TRAVEL_COMMENTS + ACCOMMODATION_COMMENTS + FOOD_COMMENTS


def get_comments_by_category(category: str) -> list:
    """
    Get sample comments by category.
    
    Args:
        category: One of 'travel', 'accommodation', 'food', 'mixed', or 'all'
                  (also supports legacy names: 'airline', 'hotel')
        
    Returns:
        List of sample comments
    """
    category = category.lower()
    
    if category in ['travel', 'airline']:
        return TRAVEL_COMMENTS
    elif category in ['accommodation', 'hotel']:
        return ACCOMMODATION_COMMENTS
    elif category == 'food':
        return FOOD_COMMENTS
    elif category == 'mixed':
        return MIXED_COMMENTS
    elif category == 'all':
        return ALL_COMMENTS
    else:
        raise ValueError(f"Unknown category: {category}. Use 'travel', 'accommodation', 'food', 'mixed', or 'all'")


def print_sample_comments():
    """Print all sample comments organized by category."""
    print("\n" + "="*80)
    print("SAMPLE CUSTOMER COMMENTS")
    print("="*80)
    
    print("\n--- TRAVEL COMMENTS ---")
    for i, comment in enumerate(TRAVEL_COMMENTS, 1):
        print(f"{i}. {comment}")
    
    print("\n--- ACCOMMODATION COMMENTS ---")
    for i, comment in enumerate(ACCOMMODATION_COMMENTS, 1):
        print(f"{i}. {comment}")
    
    print("\n--- FOOD COMMENTS ---")
    for i, comment in enumerate(FOOD_COMMENTS, 1):
        print(f"{i}. {comment}")
    
    print("\n" + "="*80)
    print(f"Total comments: {len(ALL_COMMENTS)}")
    print("="*80 + "\n")


if __name__ == "__main__":
    print_sample_comments()
