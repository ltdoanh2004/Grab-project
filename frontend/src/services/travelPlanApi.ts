import apiClient from './apiService';
import {
  AuthResponse,
  LoginPayload,
  RegisterPayload,
  SuggestionsResponse,
  TripPlanResponse,
  ActivityDetail,
  ActivityDetailResponse,
  ActivityComment
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
    
    const tripId = res.data.data.trip_id || "trip-" + Date.now();
    
    localStorage.setItem(`userInput_${tripId}`, JSON.stringify(userInput));
    
    return res.data;
  } catch (error) {
    console.error("Error fetching suggestions:", error);
    throw error;
  }
}

export async function getTripById(tripId: string): Promise<SuggestionsResponse> {
  try {
    console.log(`[API] Fetching trip data for ID: ${tripId}`);
    const res = await apiClient.get<SuggestionsResponse>(`/trip/${tripId}`);
    return res.data;
  } catch (error) {
    console.error(`Error fetching trip ${tripId}:`, error);
    throw error;
  }
}

export async function getActivityDetail(type: string, id: string): Promise<ActivityDetail> {
  try {
    const res = await apiClient.get<ActivityDetailResponse>(`/detail/${type}/${id}`);
    return res.data.data;
  } catch (error) {
    console.error(`Error fetching ${type} detail for ${id}:`, error);
    throw error;
  }
}

// Interface for comment API responses
interface CommentResponse {
  message: string;
  data: ActivityComment[];
}

// Create a comment for an activity
export async function createComment(activityId: string, commentMessage: string, type: string) {
  try {
    console.log(`API: Creating comment for ${type} with ID: ${activityId}`);
    
    // The API expects this exact format
    const requestData = {
      activity_id: activityId,
      comment_message: commentMessage,
      type: type
    };
    
    console.log('API: Sending comment request with data:', requestData);
    const res = await apiClient.post<CommentResponse>('/comment/create', requestData);
    return res.data;
  } catch (error) {
    console.error(`Error creating comment for activity ${activityId}:`, error);
    throw error;
  }
}

// Get comments for an activity
export async function getActivityComments(activityId: string, type: string) {
  try {
    console.log(`API: Getting comments for ${type} with ID: ${activityId}`);
    
    let endpoint = `/comment/activity/${activityId}`;
    

    
    console.log(`API: Requesting endpoint: ${endpoint}`);
    const res = await apiClient.get<CommentResponse>(endpoint);
    return res.data;
  } catch (error) {
    console.error(`Error fetching comments for activity ${activityId}:`, error);
    throw error;
  }
}


