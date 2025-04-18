export interface Destination {
  id: string;
  name: string;
  country: string;
  description: string;
  imageUrl: string;
  rating: number;
}
export interface TravelDate {
  startDate: Date;
  endDate: Date;
  months: number;
  length: number;
}

export interface budget {
  total: number;
  accommodation: number;
  food: number;
  activities: number;
  transportation: number;
  other: number;
}
