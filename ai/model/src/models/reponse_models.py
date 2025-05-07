from pydantic import BaseModel

class SuggestWithIDAndType(BaseModel):
    name: str
    type: str
    args: str
    id: str