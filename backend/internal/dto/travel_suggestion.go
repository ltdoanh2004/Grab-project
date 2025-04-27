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

type ActivitySuggestion struct {
	ActivityID    string  `json:"activity_id"`
	DestinationID string  `json:"destination_id"`
	CategoryID    string  `json:"category_id"`
	Name          string  `json:"name"`
	Description   string  `json:"description"`
	Duration      int     `json:"duration"`
	Cost          float64 `json:"cost"`
	ImageURL      string  `json:"image_url"`
	PlaceID       string  `json:"place_id"`
}
type ActivitiesSuggestion struct {
	Activities []ActivitySuggestion `json:"activities"`
}

type RestaurantSuggestion struct {
	RestaurantID      string  `json:"restaurant_id"`
	DestinationID     string  `json:"destination_id"`
	Name              string  `json:"name"`
	EstablishmentType string  `json:"establishment_type"`
	CuisineType       string  `json:"cuisine_type"`
	Description       string  `json:"description"`
	Address           string  `json:"address"`
	PriceRange        string  `json:"price_range"`
	AvgRating         float64 `json:"avg_rating"`
	OpeningHours      string  `json:"opening_hours"`
	ImageURL          string  `json:"image_url"`
}
type RestaurantsSuggestion struct {
	Restaurants []RestaurantSuggestion `json:"restaurants"`
}

type AccommodationSuggestion struct {
	AccommodationID string           `json:"accommodation_id"`
	DestinationID   string           `json:"destination_id"`
	Name            string           `json:"name"`
	Location        string           `json:"location"`
	City            string           `json:"city"`
	Price           float64          `json:"price"`
	Rating          float64          `json:"rating"`
	Description     string           `json:"description"`
	Link            string           `json:"booking_link"`
	Images          []model.Image    `json:"image_url"`
	RoomTypes       []model.RoomType `json:"room_types"`
	RoomInfo        string           `json:"room_info"`
	Unit            string           `json:"unit"`
	TaxInfo         string           `json:"tax_info"`
	ElderlyFriendly bool             `json:"elderly_friendly"`
}

type AccommodationsSuggestion struct {
	Accommodations []AccommodationSuggestion `json:"accommodations"`
}
