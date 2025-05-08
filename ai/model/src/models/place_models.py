from pydantic import BaseModel
from typing import List
from .accommodation_models import ImageInfo

class Location(BaseModel):
    lat: float
    lon: float

class Place(BaseModel):
    place_id: str
    name: str
    description: str
    address: str
    main_image: str
    images: List[ImageInfo]
    rating: float
    price: str
    opening_hours: str
    type: str
    categories: str
    url: str
    destination_id: str
    reviews: List[str]
    duration: str

class PlaceData(BaseModel):
    places: List[Place] 