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
  total: number;
  accommodation: number;
  food: number;
  activities: number;
  transportation: number;
  other: number;
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
