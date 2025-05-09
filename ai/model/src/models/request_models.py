from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BudgetInfo(BaseModel):
    type: str
    exactBudget: Optional[int] = Field(default=None, alias="exact_budget")

class PeopleInfo(BaseModel):
    adults: int
    children: int
    infants: int
    pets: int

class TravelTimeInfo(BaseModel):
    type: str
    startDate: datetime = Field(alias="start_date")
    endDate: datetime = Field(alias="end_date")

class PersonalOption(BaseModel):
    type: str
    name: str
    description: str

class TripSuggestionRequest(BaseModel):
    destination_id: str
    budget: BudgetInfo
    people: PeopleInfo
    travelTime: TravelTimeInfo = Field(alias="travel_time")
    personalOptions: List[PersonalOption] = Field(alias="personal_options")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True