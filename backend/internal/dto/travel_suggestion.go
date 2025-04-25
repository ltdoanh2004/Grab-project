package dto

import "skeleton-internship-backend/internal/model"

type TravelPreference struct {
	Location     string   `json:"location"`
	TravelStyle  string   `json:"travel_style"`
	Activities   []string `json:"activities"`
	Budget       string   `json:"budget"`
	DurationDays int      `json:"duration_days"`
	Season       string   `json:"season"`
	Limit        int      `json:"limit"`
}

type TravelSuggestionResponse struct {
	IDs []string `json:"ids"`
}

type ActivitiesSuggestion struct {
	Activities []model.Activity `json:"activities"`
}

type RestaurantSuggestion struct {
	Restaurants []model.Restaurant `json:"restaurants"`
}

type AccommodationSuggestion struct {
	Accommodations []model.Accommodation `json:"hotels"`
}
