import os
import sys
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from src.utils.logger import setup_logger
from src.agents.comment_agent import CommentAgent
from src.models.fix_comment_models import FixCommentResponse
model = CommentAgent()

logger = setup_logger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(ENV_PATH)

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

router = APIRouter(tags=["Fix activity based on comment"])




@router.post("/fix_activity", response_model=FixCommentResponse)
async def fix_activity(request: dict):
    """
    Endpoint to fix activity based on comment
    """
    try:
        logger.info(f"Received raw trip plan request: {request.keys()}")
        response = model.fix_activity(request)
        return FixCommentResponse(success=True, message="Activity fixed successfully", data=response)

    except Exception as e:
        logger.error(f"Error in fix_activity: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
        

