import openai
import logging
import os
from dotenv import load_dotenv
# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)


class PlanModel:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPEN_API_KEY"))
        self.model = "gpt-3.5-turbo"

    def generate_plan(self, destination: str, budget: str, people: str, travel_time: str) -> str:
        """
        Generate a travel plan based on the given destination, budget, people, and travel time.
        """
        try:
        