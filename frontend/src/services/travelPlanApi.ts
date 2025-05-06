import axios from "axios";
import {
  AuthResponse,
  LoginPayload,
  RegisterPayload,
  SuggestionsResponse,
  TripPlanResponse,
} from "../types/apiType";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8081/api/v1";

export async function register(
  payload: RegisterPayload
): Promise<AuthResponse> {
  const res = await axios.post<AuthResponse>(
    `${API_BASE_URL}/auth/register`,
    payload
  );
  return res.data;
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  const res = await axios.post<AuthResponse>(
    `${API_BASE_URL}/auth/login`,
    payload
  );
  return res.data;
}

export async function getAllSuggestions(): Promise<SuggestionsResponse> {
  try {
    const userInput = JSON.parse(localStorage.getItem("planUserInput") || "{}");

    const res = await axios.post<SuggestionsResponse>(
      `${API_BASE_URL}/suggest/all`,
      userInput,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    return res.data;
  } catch (error) {
    console.error("Error fetching suggestions:", error);
    throw error;
  }
}

export async function getTripPlan(
  suggestionData?: any,
  tripId?: string
): Promise<TripPlanResponse> {
  try {
    // Build the request payload using provided suggestion data
    const payload = {
      ...(suggestionData || {}), // Use provided suggestion data directly
      ...(tripId ? { trip_id: tripId } : {}), // Add trip_id if provided
    };

    const res = await axios.post<TripPlanResponse>(
      `${API_BASE_URL}/trip/get_plan`,
      payload,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    return res.data;
  } catch (error) {
    console.error("Error fetching trip plan:", error);
    throw error;
  }
}
