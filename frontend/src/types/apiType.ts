export interface RegisterPayload {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  username: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface AuthResponse {
  message: string;
  data: {
    access_token: string;
    refresh_token: string;
  };
}

interface ImageObject {
  url: string;
  alt: string;
}

interface RoomType {
  name: string;
  bed_type: string;
  occupancy: string;
  price: string;
  conditions: string;
  tax_and_fee: string;
}

interface Accommodation {
  accommodation_id: string;
  name: string;
  description: string;
  city: string;
  location: string;
  image_url: ImageObject[];
  price: number;
  unit: string;
  rating: number;
  booking_link: string;
  destination_id: string;
  elderly_friendly: boolean;
  room_info: string;
  room_types: RoomType[];
  tax_info: string;
}

interface Place {
  place_id: string;
  name: string;
  description: string;
  address: string;
  type: string;
  categories: string;
  main_image: string;
  images: ImageObject[];
  opening_hours: string;
  price: number;
  unit: string;
  rating: number;
  duration: string;
  reviews: string[];
  url: string;
  destination_id: string;
}

interface ServiceObject {
  name: string;
  type: number;
  url: string;
}

interface Location {
  lat: number;
  lon: number;
}

interface Restaurant {
  restaurant_id: string;
  name: string;
  description: string;
  address: string;
  cuisines: string;
  price_range: string;
  rating: number;
  photo_url: string;
  opening_hours: string;
  is_opening: boolean;
  is_booking: boolean;
  is_delivery: boolean;
  phone: string;
  url: string;
  location: Location;
  services: ServiceObject[];
  reviews: string;
  destination_id: string;
}

export interface SuggestionsResponse {
  message: string;
  data: {
    accommodation: {
      accommodations: Accommodation[];
    };
    places: {
      places: Place[];
    };
    restaurants: {
      restaurants: Restaurant[];
    };
  };
}

export interface TripActivity {
  id: string;
  type: "accommodation" | "place" | "restaurant";
  name: string;
  start_time: string;
  end_time: string;
  description: string;
  rating: number;
  address?: string;
  categories?: string;
  duration?: string;
  opening_hours?: string;
  price?: number;
  cuisines?: string;
  price_range?: string;
}

export interface DaySegment {
  time_of_day: "morning" | "afternoon" | "evening";
  activities: TripActivity[];
}

export interface DayPlan {
  date: string;
  day_title: string;
  segments: DaySegment[];
}

export interface TripPlanResponse {
  message: string;
  data: {
    user_id: string;
    trip_name: string;
    start_date: string;
    end_date: string;
    destination: string;
    plan_by_day: DayPlan[];
  };
}
