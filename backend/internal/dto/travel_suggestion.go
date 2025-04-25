package dto

import "skeleton-internship-backend/internal/model"

type TravelPreference struct {
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
