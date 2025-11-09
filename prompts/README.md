"""
Prompt Template Configuration
------------------------------
Documentation for managing external prompt templates.
"""

# This file documents the available prompt templates and their customization options.

# CLASSIFICATION PROMPT (classification_prompt.txt)
# --------------------------------------------------
# Purpose: Categorize customer comments into AIRLINE, HOTEL, or FOOD
# Input Variables: {comment}
# Expected Output: One of: AIRLINE, HOTEL, FOOD
#
# Customization Tips:
# - Add more categories by including them in the list
# - Modify the instruction style for different models
# - Add examples for few-shot learning
#
# Example customization:
"""
Classify the following customer comment into ONE of these categories: 
AIRLINE, HOTEL, FOOD, CAR_RENTAL, or TOUR_PACKAGE.

Provide ONLY the category name in uppercase.

Examples:
- "Flight was delayed" -> AIRLINE
- "Room was clean" -> HOTEL
- "Food was delicious" -> FOOD

Customer comment: {comment}

Category:
"""


# SENTIMENT PROMPT (sentiment_prompt.txt)
# ----------------------------------------
# Purpose: Analyze sentiment of customer comments
# Input Variables: {comment}
# Expected Output: One of: POSITIVE, NEGATIVE, NEUTRAL
#
# Customization Tips:
# - Add more sentiment granularity (e.g., VERY_POSITIVE, SLIGHTLY_NEGATIVE)
# - Include confidence scores in the output
# - Add reasoning or explanation requests
#
# Example customization:
"""
Analyze the sentiment of the following customer comment.
Classify it as one of: VERY_POSITIVE, POSITIVE, NEUTRAL, NEGATIVE, or VERY_NEGATIVE.

Consider the tone, word choice, and overall message.
Respond with only the sentiment category in uppercase.

Customer comment: {comment}

Sentiment:
"""


# ADDING NEW TEMPLATES
# ---------------------
# 1. Create a new .txt file in the prompts/ directory
# 2. Use {variable_name} syntax for placeholders
# 3. Update CustomerCommentAnalyzer class to load the new template
# 4. Create a new chain using the loaded template
#
# Example:
# File: prompts/urgency_prompt.txt
"""
Determine the urgency level of this customer comment.
Classify it as: HIGH, MEDIUM, or LOW urgency.

Customer comment: {comment}

Urgency:
"""
# Then in code:
# urgency_template = self._load_prompt_template("urgency_prompt.txt")
# self.urgency_prompt = PromptTemplate(input_variables=["comment"], template=urgency_template)
# self.urgency_chain = LLMChain(llm=self.llm, prompt=self.urgency_prompt)


# BEST PRACTICES
# ---------------
# 1. Keep prompts clear and concise
# 2. Specify output format explicitly
# 3. Use consistent terminology
# 4. Test prompts with various inputs
# 5. Version control your prompt changes
# 6. Document any special requirements or constraints
