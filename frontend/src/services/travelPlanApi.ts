import apiClient from './apiService';
import {
  AuthResponse,
  LoginPayload,
  RegisterPayload,
  SuggestionsResponse,
  TripPlanResponse,
} from "../types/apiType";
import { DESTINATION_MAPPINGS } from "../constants/destinationConstants";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8081/api/v1";

export async function register(
  payload: RegisterPayload
): Promise<AuthResponse> {
  const res = await apiClient.post<AuthResponse>("/auth/register", payload);
  return res.data;
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  const res = await apiClient.post<AuthResponse>("/auth/login", payload);
  return res.data;
}

export async function getAllSuggestions(): Promise<SuggestionsResponse> {
  try {
    const userInput = JSON.parse(localStorage.getItem("planUserInput") || "{}");
    
    const destinationId = userInput.destination ? 
      DESTINATION_MAPPINGS[userInput.destination] || userInput.destination : 
      "";

    const transformedInput = {
      destination_id: destinationId,
      budget: {
        type: userInput.budget?.type || "",
        exact_budget: userInput.budget?.exactBudget || 0
      },
      people: userInput.people || {
        adults: 0,
        children: 0,
        infants: 0,
        pets: 0
      },
      travel_time: {
        type: userInput.travelTime?.type || "",
        start_date: userInput.travelTime?.startDate || "",
        end_date: userInput.travelTime?.endDate || ""
      },
      personal_options: userInput.personalOptions || [],
      travel_preference_id: "leisure", 
      trip_id: "temp-" + Date.now() 
    };

    console.log("[API] Sending request to /suggest/trip");

    const res = await apiClient.post<SuggestionsResponse>(
      "/suggest/trip",
      transformedInput
    );

    return res.data;
  } catch (error) {
    console.error("Error fetching suggestions:", error);
    throw error;
  }
}

export async function getCompletePlan(tripId: string): Promise<SuggestionsResponse> {
  try {
    const res = await apiClient.get<SuggestionsResponse>(
      `/trip/${tripId}`
    );
    return res.data;
  } catch (error) {
    console.error("Error fetching complete plan:", error);
    throw error;
  }
}


