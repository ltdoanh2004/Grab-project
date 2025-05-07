from pydantic import BaseModel
from typing import List
from .place_models import Location

class Restaurant(BaseModel):
    restaurant_id: str
    name: str
    description: str
    address: str
    cuisines: str
    price_range: str
    rating: float
    main_image: str
    photo_url: str
    media_urls: str
    opening_hours: str
    is_opening: bool
    is_booking: bool
    is_delivery: bool
    reviews: List[str]
    num_reviews: int
    review_summary: str
    example_reviews: str
    phone: str
    url: str
    destination_id: str
    location: Location
    services: List[str]

class RestaurantData(BaseModel):
    restaurants: List[Restaurant] 