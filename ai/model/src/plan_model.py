"""travel_planner.py – rebuilt for explicit JSON output
=================================================================
This version drops the earlier Pydantic schema and instead forces the
LLM to return a **single valid JSON object** that exactly matches the
shape FE/BE yêu cầu (trip_name, start_date, … plan_by_day → segments →
activities …).

Key points
-----------
* `JSON_SCHEMA_EXAMPLE` holds a *minimal* skeleton of the structure and
  is embedded straight into the prompt.
* `JsonOutputParser` (LangChain) post‑validates the LLM response and
  returns a native Python dict you can hand to FE / persist to DB.
* A helper `TravelPlanner.generate_plan` takes the consolidated
  `input_data = {"accommodations": [...], "places": [...], "restaurants": [...]}`.
  + You can optionally pass `trip_name`, `start_date`, `end_date`, `user_id`.
* Ready stubs (`WeatherTool`, `MapTool`) illustrate cách add tools sau
  này – chỉ cần bổ sung `func` thật và liệt kê vào `TOOLS`.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.chains import LLMChain
from langchain.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI

# ---------------------------------------------------------------------------
# 🔧 ENV & Logging
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger("travel_planner")

# ---------------------------------------------------------------------------
# 📜 Example JSON schema we expect from LLM
# ---------------------------------------------------------------------------
JSON_SCHEMA_EXAMPLE = {
    "trip_name": "<string – ex: Đà Nẵng nghỉ dưỡng 4 ngày>",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "user_id": "<string>",
    "destination": "<string>",
    "plan_by_day": [
        {
            "date": "YYYY-MM-DD",
            "day_title": "<string>",
            "segments": [
                {
                    "time_of_day": "morning | afternoon | evening | night",
                    "activities": [
                        {
                            "id": "<string>",
                            "type": "accommodation | place | restaurant",
                            "name": "<string>",
                            "start_time": "HH:MM",
                            "end_time": "HH:MM",
                            "description": "<string>",
                            "location": "<string>",
                            "rating": "<number>",
                            "price": "<number or string>",
                            "image_url": "<string>",
                            "url": "<string>"
                            # (các trường extra nếu có)
                        }
                    ]
                }
            ]
        }
    ]
}

FORMAT_INSTRUCTIONS = (
    "Respond ONLY with VALID minified JSON (no markdown) that matches "
    "exactly the structure & keys of the following example: "
    f"{json.dumps(JSON_SCHEMA_EXAMPLE, ensure_ascii=False)}"
)

json_parser = JsonOutputParser()

# ---------------------------------------------------------------------------
# 🛠️  Optional tools stubs – plug real API later
# ---------------------------------------------------------------------------

def dummy_weather_tool(query: str) -> str:  # pragma: no cover
    """Placeholder weather tool."""
    return "{\"temp\":30, \"condition\":\"sunny\"}"

TOOLS: List[Tool] = [
    Tool(name="weather", func=dummy_weather_tool, description="Lấy dữ liệu thời tiết"),
]

# ---------------------------------------------------------------------------
# 🚂  Planner class
# ---------------------------------------------------------------------------


class PlanModel:
    def __init__(self, temperature: float = 0.7):
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=temperature)
        self.parser = json_parser  # langchain JSON parser

    # ---------------------------------------------------------------------
    # 🔑 Prompt builder
    # ---------------------------------------------------------------------
    def _build_prompt(self) -> PromptTemplate:
        template = (
            "You are an expert Vietnamese travel planner. Using the user data, "
            "generate a coherent multi‑day trip strictly in JSON format.\n\n"
            "User context (JSON): {user_json}\n\n" + FORMAT_INSTRUCTIONS
        )
        return PromptTemplate(template=template, input_variables=["user_json"])

    # ------------------------------------------------------------------
    # 🧩  Plain chain (no external tools)
    # ------------------------------------------------------------------
    def generate_plan(self, input_data: Dict[str, Any], **meta: Any) -> Dict[str, Any]:
        """LLM only – returns parsed JSON dict."""
        log.info("Generating plan (no agent)…")
        chain = LLMChain(llm=self.llm, prompt=self._build_prompt())
        raw = chain.run(user_json=json.dumps({**input_data, **meta}, ensure_ascii=False))
        return self.parser.parse(raw)

    # ------------------------------------------------------------------
    # 🤖  Agent‑based generation (tool‑ready)
    # ------------------------------------------------------------------
    def generate_plan_with_tools(
        self, input_data: Dict[str, Any], **meta: Any
    ) -> Dict[str, Any]:
        """Agent that can call external tools (weather, maps, etc.)."""
        log.info("Generating plan with agent/tools…")
        agent = initialize_agent(
            TOOLS, self.llm, agent="zero-shot-react-description", verbose=False
        )
        # We still enforce output JSON via explicit directive.
        prompt = self._build_prompt().format(user_json=json.dumps({**input_data, **meta}, ensure_ascii=False))
        raw = agent.run(prompt)  # agent can decide to call tools
        return self.parser.parse(raw)


# ---------------------------------------------------------------------------
# 🧪 CLI quick test (python travel_planner.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_input = {
        "accommodations": [{"id": "hotel42", "name": "Sala", "price": 850000}],
        "places": [{"id": "place10", "name": "Bãi biển Mỹ Khê"}],
        "restaurants": [{"id": "fnb12", "name": "Nhà hàng Bé Mặn"}],
    }
    planner = PlanModel()
    plan = planner.generate_plan(sample_input, trip_name="Test", destination="Đà Nẵng")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
