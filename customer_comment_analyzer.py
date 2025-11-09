"""
Customer Comment Analyzer
--------------------------
An intelligent application that classifies customer comments into categories
(airline, hotel, food) and analyzes sentiment using LangChain and Hugging Face LLMs.
"""

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
import os
import sys
import traceback
from typing import List, Dict
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class CustomerCommentAnalyzer:
    """
    Analyzes customer comments for category classification and sentiment analysis.
    """
    
    def __init__(self, hf_token: str = None, prompts_dir: str = None):
        """
        Initialize the analyzer with Hugging Face models.
        
        Args:
            hf_token: Hugging Face API token (optional, can use HF_TOKEN env variable)
            prompts_dir: Directory containing prompt template files (optional)
        """
        # Set up Hugging Face token
        if hf_token:
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token
        
        # Set prompts directory
        if prompts_dir is None:
            # Default to 'prompts' directory relative to this file
            current_dir = Path(__file__).parent
            self.prompts_dir = current_dir / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        # Initialize Hugging Face LLM using Chat interface
        # Using Meta Llama model which is widely available
        llm_endpoint = HuggingFaceEndpoint(
            repo_id="meta-llama/Llama-3.2-3B-Instruct",
            task="conversational",
            huggingfacehub_api_token=hf_token or os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
            temperature=0.1,
            max_new_tokens=50
        )
        
        # Wrap in ChatHuggingFace for better instruction following
        self.llm = ChatHuggingFace(llm=llm_endpoint)
        
        # Load prompt templates from external files
        classification_template = self._load_prompt_template("classification_prompt.txt")
        sentiment_template = self._load_prompt_template("sentiment_prompt.txt")
        
        # Create classification chain using LCEL (LangChain Expression Language)
        self.classification_prompt = PromptTemplate(
            input_variables=["comment"],
            template=classification_template
        )
        
        self.classification_chain = self.classification_prompt | self.llm
        
        # Create sentiment analysis chain using LCEL
        self.sentiment_prompt = PromptTemplate(
            input_variables=["comment"],
            template=sentiment_template
        )
        
        self.sentiment_chain = self.sentiment_prompt | self.llm
    
    def _load_prompt_template(self, filename: str) -> str:
        """
        Load a prompt template from an external file.
        
        Args:
            filename: Name of the template file in the prompts directory
            
        Returns:
            Template string content
        """
        template_path = self.prompts_dir / filename
        
        if not template_path.exists():
            raise FileNotFoundError(
                f"Prompt template file not found: {template_path}\n"
                f"Please ensure the file exists in the prompts directory."
            )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read().strip()
        
        return template
    
    def classify_comment(self, comment: str) -> str:
        """
        Classify a customer comment into travel, accommodation, or food category.
        
        Args:
            comment: The customer comment text
            
        Returns:
            Category classification (TRAVEL, ACCOMMODATION, or FOOD)
        """
        try:
            result = self.classification_chain.invoke({"comment": comment})
            # Extract content from AIMessage if needed
            if hasattr(result, 'content'):
                category = result.content.strip().upper()
            else:
                category = result.strip().upper()
            
            # Extract category from response
            if 'TRAVEL' in category:
                return 'TRAVEL'
            elif 'ACCOMMODATION' in category:
                return 'ACCOMMODATION'
            elif 'FOOD' in category:
                return 'FOOD'
            # Handle legacy category names
            elif 'AIRLINE' in category:
                return 'TRAVEL'
            elif 'HOTEL' in category:
                return 'ACCOMMODATION'
            else:
                # Return first word if unclear
                return category.split()[0] if category else 'UNKNOWN'
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error classifying comment: {e}", file=sys.stderr)
            print(f"Traceback: {error_details}", file=sys.stderr)
            return 'UNKNOWN'
    
    def analyze_sentiment(self, comment: str) -> str:
        """
        Analyze the sentiment of a customer comment.
        
        Args:
            comment: The customer comment text
            
        Returns:
            Sentiment classification (POSITIVE, NEGATIVE, or NEUTRAL)
        """
        try:
            result = self.sentiment_chain.invoke({"comment": comment})
            # Extract content from AIMessage if needed
            if hasattr(result, 'content'):
                sentiment = result.content.strip().upper()
            else:
                sentiment = result.strip().upper()
            
            # Extract sentiment from response
            if 'POSITIVE' in sentiment:
                return 'POSITIVE'
            elif 'NEGATIVE' in sentiment:
                return 'NEGATIVE'
            elif 'NEUTRAL' in sentiment:
                return 'NEUTRAL'
            else:
                # Return first word if unclear
                return sentiment.split()[0] if sentiment else 'NEUTRAL'
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error analyzing sentiment: {e}", file=sys.stderr)
            print(f"Traceback: {error_details}", file=sys.stderr)
            return 'NEUTRAL'
    
    def analyze_comment(self, comment: str) -> Dict[str, str]:
        """
        Perform complete analysis on a comment (classification + sentiment).
        
        Args:
            comment: The customer comment text
            
        Returns:
            Dictionary with comment, category, and sentiment
        """
        category = self.classify_comment(comment)
        sentiment = self.analyze_sentiment(comment)
        
        return {
            'comment': comment,
            'category': category,
            'sentiment': sentiment
        }
    
    def analyze_batch(self, comments: List[str]) -> List[Dict[str, str]]:
        """
        Analyze a batch of customer comments.
        
        Args:
            comments: List of customer comment texts
            
        Returns:
            List of dictionaries with analysis results
        """
        results = []
        for i, comment in enumerate(comments, 1):
            print(f"\nAnalyzing comment {i}/{len(comments)}...")
            result = self.analyze_comment(comment)
            results.append(result)
        
        return results
    
    def print_results(self, results: List[Dict[str, str]]):
        """
        Print analysis results in a formatted way.
        
        Args:
            results: List of analysis results
        """
        print("\n" + "="*80)
        print("CUSTOMER COMMENT ANALYSIS RESULTS")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            print(f"\n--- Comment {i} ---")
            print(f"Text: {result['comment']}")
            print(f"Category: {result['category']}")
            print(f"Sentiment: {result['sentiment']}")
        
        print("\n" + "="*80)
        
        # Summary statistics
        categories = {}
        sentiments = {}
        
        for result in results:
            cat = result['category']
            sent = result['sentiment']
            categories[cat] = categories.get(cat, 0) + 1
            sentiments[sent] = sentiments.get(sent, 0) + 1
        
        print("\nSUMMARY STATISTICS")
        print("-" * 80)
        print("\nCategory Distribution:")
        for category, count in sorted(categories.items()):
            percentage = (count / len(results)) * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")
        
        print("\nSentiment Distribution:")
        for sentiment, count in sorted(sentiments.items()):
            percentage = (count / len(results)) * 100
            print(f"  {sentiment}: {count} ({percentage:.1f}%)")
        
        print("="*80)


def main():
    """
    Main function to demonstrate the customer comment analyzer.
    """
    # Check if HF token is available
    hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    
    if not hf_token:
        print("\n⚠️  Warning: No Hugging Face token found!")
        print("Please set your Hugging Face API token:")
        print("1. Get your token from: https://huggingface.co/settings/tokens")
        print("2. Set it as environment variable: $env:HUGGINGFACEHUB_API_TOKEN='your_token_here'")
        print("   Or pass it directly to CustomerCommentAnalyzer(hf_token='your_token')\n")
        
        # Allow user to input token
        user_token = input("Enter your Hugging Face token (or press Enter to exit): ").strip()
        if not user_token:
            print("Exiting...")
            return
        hf_token = user_token
    
    # Sample comments for testing
    sample_comments = [
        "The flight was delayed by 3 hours and the staff was very rude. Worst experience ever!",
        "Hotel room was clean and spacious. The breakfast buffet was amazing!",
        "The pasta was undercooked and the service was slow. Very disappointed.",
        "Great airline! The seats were comfortable and the crew was friendly.",
        "The hotel location is perfect, right in the city center. Would definitely stay again!",
        "Food arrived cold and tasted bland. Not worth the price.",
        "Smooth flight with on-time departure and arrival. Impressed!",
        "Room service was excellent but the bed was uncomfortable.",
        "The restaurant ambiance is nice but the portions are too small."
    ]
    
    print("\n🚀 Initializing Customer Comment Analyzer...")
    print("This may take a moment as we load the AI model...\n")
    
    # Initialize analyzer
    analyzer = CustomerCommentAnalyzer(hf_token=hf_token)
    
    # Analyze comments
    results = analyzer.analyze_batch(sample_comments)
    
    # Print results
    analyzer.print_results(results)


if __name__ == "__main__":
    main()
