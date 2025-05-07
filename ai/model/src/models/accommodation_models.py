from pydantic import BaseModel
from typing import List

class ImageInfo(BaseModel):
    url: str
    alt: str

class RoomType(BaseModel):
    name: str
    bed_type: str
    occupancy: str
    price: str
    tax_and_fee: str
    conditions: str

class Accommodation(BaseModel):
    accommodation_id: str
    name: str
    description: str
    location: str
    city: str
    image_url: List[ImageInfo]
    price: float
    unit: str
    rating: float
    destination_id: str
    booking_link: str
    elderly_friendly: bool
    room_info: str
    room_types: List[RoomType]
    tax_info: str

class AccommodationData(BaseModel):
    accommodations: List[Accommodation] 