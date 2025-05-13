export const ItemTypes = { ACTIVITY: "activity" } as const;

export interface DragItem {
  type: string;
  id: string;
  dayId: number;
  index: number;
}

export interface Destination {
  id: string;
  name: string;
  country: string;
  description: string;
  imageUrl: string;
  rating: number;
}

export interface ExactTime {
  type: "exact";
  startDate: Date | null;
  endDate: Date | null;
}

export interface FlexibleTime {
  type: "flexible";
  month: number;
  length: number;
}

export type TravelTime = ExactTime | FlexibleTime;

export interface Budget {
  type: "$" | "$$" | "$$$" | "$$$$" | "$$$$$";
  exactBudget?: number;
}

export interface NumOfPeople {
  adults: number;
  children: number;
  infants: number;
  pets: number;
}

export interface PersonalOption {
  type: "places" | "activities" | "food" | "transportation" | "accommodation";
  description: string;
  name: string;
  imageUrl?: string;
}

export interface PersonalOptions {
  places: PersonalOption[];
  activities: PersonalOption[];
  food: PersonalOption[];
  transportation: PersonalOption[];
  accommodation: PersonalOption[];
}

export interface TravelActivity {
  id: string;
  activity_id?: string;
  type: string;
  name: string;
  imgUrl?: string;
  image_url?: string;
  image_urls?: string[];
  start_time: string;
  end_time: string;
  description: string;
  rating?: number;
  cuisines?: string;
  price_range?: string;
  price?: number;
  address?: string;
  categories?: string;
  duration?: string;
  opening_hours?: string;
  price_ai_estimate?: number;
  additional_info?: string;
  url?: string;
  location?: string;
}

export interface TravelSegment {
  time_of_day: string;
  activities: TravelActivity[];
}

export interface TravelDay {
  date: string;
  day_title: string;
  segments: TravelSegment[];
  daily_tips?: string[];
}

export interface TravelDetailData {
  id?: string;
  trip_id?: string;
  user_id: string;
  trip_name: string;
  start_date: string;
  end_date: string;
  destination: string;
  destination_id?: string;
  plan_by_day: TravelDay[];

  // Faked/optional fields for UI compatibility
  adults?: number;
  children?: number;
  budgetType?: "$" | "$$" | "$$$" | "$$$$" | "$$$$$";
  totalBudget?: number;
  spentBudget?: number;
  status?: "planning" | "confirmed" | "completed" | "canceled" | "upcoming";
  notes?: string;
  imageUrl?: string;
}
