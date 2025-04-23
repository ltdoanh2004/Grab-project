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
  time: string;
  type: "attraction" | "restaurant" | "hotel" | "transport";
  name: string;
  location: string;
  description: string;
  imageUrl: string;
  rating: number;
  price?: number | string;
  contactInfo?: string;
  duration?: number;
}

export interface TravelDay {
  day: number;
  date: Date;
  activities: TravelActivity[];
}

export interface TravelDetailData {
  id: string;
  destination: string;
  imageUrl: string;
  startDate: Date;
  endDate: Date;
  adults: number;
  children: number;
  budgetType: "$" | "$$" | "$$$" | "$$$$" | "$$$$$";
  totalBudget: number;
  spentBudget: number;
  status: "planning" | "confirmed" | "completed" | "canceled" | "upcoming";
  notes: string;
  days: TravelDay[];
}
