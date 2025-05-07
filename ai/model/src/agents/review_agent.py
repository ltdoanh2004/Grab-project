from typing import List, Optional
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.tools.tavily_search import TavilySearchResults
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TravelTipAggregator:
    def __init__(self, openai_api_key: Optional[str] = None, tavily_api_key: Optional[str] = None):
        """
        Initialize the TravelTipAggregator agent.
        
        Args:
            openai_api_key: OpenAI API key (optional, will use env var if not provided)
            tavily_api_key: Tavily API key (optional, will use env var if not provided)
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        if not self.tavily_api_key:
            raise ValueError("Tavily API key is required")
            
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.5,
            openai_api_key=self.openai_api_key
        )
        
        self._setup_tools()
        self._setup_agent()
        
    def _setup_tools(self):
        """Set up the tools for the agent."""
        # Web search tool using Tavily
        self.search_tool = TavilySearchResults(
            api_key=self.tavily_api_key,
            max_results=3
        )
        
        # Tip extractor tool
        def extract_travel_tips_from_text(text: str) -> str:
            prompt = f"""Extract 3-5 practical travel tips for tourists visiting the following place or doing the following activity:

{text}

                    Your output should be a bullet list of short and useful tips. Focus on practical, actionable advice that would be helpful for tourists."""
            return self.llm.predict(prompt)
        
        self.tip_extractor_tool = Tool.from_function(
            func=extract_travel_tips_from_text,
            name="TipExtractor",
            description="Extract practical travel tips from travel articles or descriptions."
        )
        
        self.tools = [self.search_tool, self.tip_extractor_tool]
        
    def _setup_agent(self):
        """Set up the ReAct agent with tools and memory."""
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
        )
        
    def get_travel_tips(self, query: str) -> List[str]:
        """
        Get travel tips for a specific location or activity.
        
        Args:
            query: The search query (e.g., "Find practical travel tips for visiting Hanoi Old Quarter in the afternoon")
            
        Returns:
            List of travel tips
        """
        try:
            result = self.agent.run(query)
            # Convert the result into a list of tips
            tips = [tip.strip() for tip in result.split('\n') if tip.strip()]
            return tips
        except Exception as e:
            print(f"Error getting travel tips: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    aggregator = TravelTipAggregator()
    tips = aggregator.get_travel_tips(
        "Find practical travel tips for visiting Hanoi Old Quarter in the afternoon"
    )
    print("\nTravel Tips:")
    for tip in tips:
        print(f"- {tip}")
