from pydantic import BaseModel
class FixCommentResponse(BaseModel):
    success: bool
    message: str
    data: dict