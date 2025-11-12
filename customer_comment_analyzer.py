"""
Customer Comment Analyzer
--------------------------
An intelligent application that classifies customer comments into categories
(airline, hotel, food) and analyzes sentiment using LangChain and Azure OpenAI.

Uses LangChain tools and agent for modular analysis operations.
"""

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_agent
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
    Uses LangChain agent with tools for modular analysis operations.
    """
    
    # Constructor initializing the model and agent
    def __init__(self, azure_endpoint: str = None, api_key: str = None, deployment_name: str = None, prompts_dir: str = None):
        """
        Initialize the analyzer with Azure OpenAI and create agent.
        
        Args:
            azure_endpoint: Azure OpenAI endpoint (optional, can use AZURE_OPENAI_ENDPOINT env variable)
            api_key: Azure OpenAI API key (optional, can use AZURE_OPENAI_API_KEY env variable)
            deployment_name: Azure deployment name (optional, can use AZURE_OPENAI_DEPLOYMENT_NAME env variable)
            prompts_dir: Directory containing prompt template files (optional)
        """
        # Set prompts directory
        if prompts_dir is None:
            # Default to 'prompts' directory relative to this file
            current_dir = Path(__file__).parent
            self.prompts_dir = current_dir / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        # Initialize Azure OpenAI
        self.model = AzureChatOpenAI(
            azure_endpoint=azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=api_key or os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            deployment_name=deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            temperature=0.1,
            max_tokens=200
        )
        
        # Load prompt templates from external files
        classification_template = self._load_prompt_template("classification_prompt.txt")
        sentiment_template = self._load_prompt_template("sentiment_prompt.txt")
        
        # Create classification chain using LCEL (LangChain Expression Language)
        self.classification_prompt = PromptTemplate(
            input_variables=["comment"],
            template=classification_template
        )
        
        self.classification_chain = self.classification_prompt | self.model
        
        # Create sentiment analysis chain using LCEL
        self.sentiment_prompt = PromptTemplate(
            input_variables=["comment"],
            template=sentiment_template
        )
        
        self.sentiment_chain = self.sentiment_prompt | self.model
        
        # Create tools and agent
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """
        Create LangChain tools for classification and sentiment analysis.
        
        Returns:
            List of Tool objects
        """
        def classify_comment(comment: str) -> str:
            """Classify a customer comment into TRAVEL, ACCOMMODATION, or FOOD category"""
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
                error_details = traceback.format_exc()
                print(f"Error classifying comment: {e}", file=sys.stderr)
                print(f"Traceback: {error_details}", file=sys.stderr)
                return 'UNKNOWN'
        
        def analyze_sentiment(comment: str) -> str:
            """Analyze the sentiment of a customer comment and return POSITIVE, NEGATIVE, or NEUTRAL"""
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
        
        return [
            Tool(
                name="ClassifyComment",
                func=classify_comment,
                description=(
                    "Use this to classify a customer comment into one of three categories: "
                    "TRAVEL (for flights, airlines, airports, baggage, boarding, crew), "
                    "ACCOMMODATION (for hotels, rooms, check-in, housekeeping, amenities), or "
                    "FOOD (for restaurants, meals, dishes, cooking, taste). "
                    "Input should be the comment text as a string."
                )
            ),
            Tool(
                name="AnalyzeSentiment",
                func=analyze_sentiment,
                description=(
                    "Use this to analyze the sentiment of a customer comment. "
                    "Returns POSITIVE, NEGATIVE, or NEUTRAL based on the emotional tone. "
                    "Input should be the comment text as a string."
                )
            )
        ]
    
    def _create_agent(self):
        """
        Create agent using create_agent with model, tools, and system prompt.
        
        Returns:
            Agent instance
        """
        # Create the agent using LangChain 1.0 API
        agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt="You are a helpful customer comment analysis assistant. Use the available tools to classify comments into categories and analyze sentiment. Always use the tools to provide accurate analysis."
        )
        
        return agent
    
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
    
    def get_tools(self) -> List[Tool]:
        """
        Get the list of tools available for the agent.
        
        Returns:
            List of Tool objects
        """
        return self.tools
    
    def classify_comment(self, comment: str) -> str:
        """
        Classify a customer comment using the agent.
        
        Args:
            comment: The customer comment text
            
        Returns:
            Category classification (TRAVEL, ACCOMMODATION, or FOOD)
        """
        try:
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": f"Classify this customer comment into TRAVEL, ACCOMMODATION, or FOOD category: {comment}"}]
            })
            
            # Handle agent response - it returns a dict with 'messages' key
            if isinstance(result, dict) and "messages" in result:
                response = result["messages"][-1].content if hasattr(result["messages"][-1], 'content') else str(result["messages"][-1])
            else:
                response = result.content if hasattr(result, 'content') else str(result)
            
            # Extract category from response
            response_upper = response.upper()
            if 'TRAVEL' in response_upper:
                return 'TRAVEL'
            elif 'ACCOMMODATION' in response_upper:
                return 'ACCOMMODATION'
            elif 'FOOD' in response_upper:
                return 'FOOD'
            else:
                return response.strip()
        except Exception as e:
            print(f"Error in agent classification: {e}", file=sys.stderr)
            # Fallback to direct tool call
            return self.tools[0].func(comment)
    
    def analyze_sentiment(self, comment: str) -> str:
        """
        Analyze sentiment using the agent.
        
        Args:
            comment: The customer comment text
            
        Returns:
            Sentiment classification (POSITIVE, NEGATIVE, or NEUTRAL)
        """
        try:
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": f"Analyze the sentiment of this customer comment: {comment}"}]
            })
            
            # Handle agent response - it returns a dict with 'messages' key
            if isinstance(result, dict) and "messages" in result:
                response = result["messages"][-1].content if hasattr(result["messages"][-1], 'content') else str(result["messages"][-1])
            else:
                response = result.content if hasattr(result, 'content') else str(result)
            
            # Extract sentiment from response
            response_upper = response.upper()
            if 'POSITIVE' in response_upper:
                return 'POSITIVE'
            elif 'NEGATIVE' in response_upper:
                return 'NEGATIVE'
            elif 'NEUTRAL' in response_upper:
                return 'NEUTRAL'
            else:
                return response.strip()
        except Exception as e:
            print(f"Error in agent sentiment analysis: {e}", file=sys.stderr)
            # Fallback to direct tool call
            return self.tools[1].func(comment)
    
    def analyze_comment(self, comment: str) -> Dict[str, str]:
        """
        Perform complete analysis on a comment using the agent.
        
        Args:
            comment: The customer comment text
            
        Returns:
            Dictionary with comment, category, and sentiment
        """
        try:
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": f"Analyze this customer comment for both category and sentiment: {comment}"}]
            })
            
            # Handle agent response - it returns a dict with 'messages' key
            if isinstance(result, dict) and "messages" in result:
                response = result["messages"][-1].content if hasattr(result["messages"][-1], 'content') else str(result["messages"][-1])
            else:
                response = result.content if hasattr(result, 'content') else str(result)
            
            # Try to extract category and sentiment from response
            category = self.classify_comment(comment)
            sentiment = self.analyze_sentiment(comment)
            
            return {
                'comment': comment,
                'category': category,
                'sentiment': sentiment
            }
        except Exception as e:
            print(f"Error in agent analysis: {e}", file=sys.stderr)
            # Fallback to direct analysis
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
        for comment in comments:
            result = self.analyze_comment(comment)
            results.append(result)
        
        return results
