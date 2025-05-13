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
  data: Array<{
    access_token: string;
    refresh_token: string;
  }>;
}

export interface ImageObject {
  url: string;
  alt: string;
}

export interface RoomType {
  name: string;
  bed_type: string;
  occupancy: string;
  price: string;
  conditions: string;
  tax_and_fee: string;
}

export interface ActivityComment {
  comment_id: string;
  comment_message: string;
  user_id: string;
  username?: string;
  trip_accommodation_id?: string;
  trip_place_id?: string;
  trip_restaurant_id?: string;
  activity_id?: string;
  created_at?: string;
}

export interface TripActivity {
  id: string;
  activity_id: string;
  name: string;
  description: string;
  start_time: string;
  end_time: string;
  type: string;
  price_ai_estimate: number;
  comments?: ActivityComment[];
}

export interface DaySegment {
  time_of_day: string;
  activities: TripActivity[];
}

export interface DayPlan {
  date: string;
  day_title: string;
  daily_tips?: string[];
  segments: DaySegment[];
}

export interface SuggestionsResponse {
  message: string;
  data: {
    trip_id: string;
    trip_name?: string;
    start_date?: string;
    end_date?: string;
    destination_id?: string;
    user_id?: string;
    plan_by_day?: DayPlan[];
  };
}

export interface ActivityDetail {
  id: string;
  name: string;
  description: string;
  address: string;
  location: string;
  type: string;
  opening_hours: string;
  price: number;
  rating: number;
  image_urls: string[];
  url: string;
  additional_info: string;
}

export interface ActivityDetailResponse {
  message: string;
  data: ActivityDetail;
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
