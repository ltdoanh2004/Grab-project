from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BudgetInfo(BaseModel):
    type: str
    exactBudget: Optional[int] = None

class PeopleInfo(BaseModel):
    adults: int
    children: int
    infants: int
    pets: int

class TravelTimeInfo(BaseModel):
    type: str
    startDate: datetime
    endDate: datetime

class PersonalOption(BaseModel):
    type: str
    name: str
    description: str



class TripSuggestionRequest(BaseModel):
    destination: str
    budget: BudgetInfo
    people: PeopleInfo
    travelTime: TravelTimeInfo
    personalOptions: List[PersonalOption]