import json
import logging
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional
import time

from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.chat_models import ChatOpenAI



ROOT = Path(__file__).resolve().parent
print(ROOT)
load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger("travel_planner")

class AgentTool:
    def __init__(self):
        self.llm = OpenAI(api_key=os.getenv("OPEN_API_KEY"), temperature=0.0)
        self.parser = JsonOutputParser()
        self.agent_tool = self.get_agent_tool()

    def get_agent_tool(self):
        """
        Tạo các công cụ cho agent
        """
        
    def fix_base_on_comment(self, all_plan: Dict[str, Any], data_detail_for_element: Dict[str, Any], comment: str) -> Dict[str, Any]:
        """
        Sửa đổi kế hoạch dựa trên bình luận
        """
        prompt = PromptTemplate(
            template=self.fix_base_on_comment_prompt,
            input_variables=["plan_for_specific_element", "data_detail_for_element", "comment"]
        )
        chain = prompt | self.llm | self.parser
        return chain.invoke({"plan_for_specific_element": plan_for_specific_element, "data_detail_for_element": data_detail_for_element, "comment": comment})
    
    def get_plan_for_specific_element(self, plan: Dict[str, Any], data_detail: Dict[str, Any], element_id: str) -> Dict[str, Any]:
        
