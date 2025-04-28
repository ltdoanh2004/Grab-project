package dto

import (
	"skeleton-internship-backend/internal/util"
)

type TravelPreference struct {
	Location     string           `json:"location"`
	TravelStyle  string           `json:"travel_style"`
	Places       util.StringArray `json:"places"`
	Budget       string           `json:"budget"`
	DurationDays int              `json:"duration_days"`
	Season       string           `json:"season"`
	Limit        int              `json:"limit"`
}

type TravelSuggestionResponse struct {
	IDs util.StringArray `json:"ids"`
}

type PlaceSuggestion struct {
	PlaceID       string           `gorm:"type:char(36);primaryKey" json:"place_id"`
	DestinationID string           `gorm:"type:char(36)" json:"destination_id"`
	Name          string           `gorm:"size:100;not null" json:"name"`
	URL           string           `gorm:"size:255" json:"url"`
	Address       string           `gorm:"size:255" json:"address"`
	Duration      string           `gorm:"size:50" json:"duration"`
	Type          string           `gorm:"size:50" json:"type"`
	ImageURLs     util.ImageArray  `gorm:"type:json" json:"image_urls"`
	MainImage     string           `gorm:"size:255" json:"main_image"`
	Price         string           `gorm:"size:20" json:"price"`
	Rating        float64          `json:"rating"`
	Description   string           `gorm:"type:text" json:"description"`
	OpeningHours  string           `gorm:"type:text" json:"opening_hours"`
	Reviews       util.StringArray `gorm:"type:json" json:"reviews"`
	Categories    string           `gorm:"type:json" json:"categories"`
}
type PlacesSuggestion struct {
	Places []PlaceSuggestion `json:"places"`
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
	AccommodationID string             `json:"accommodation_id"`
	DestinationID   string             `json:"destination_id"`
	Name            string             `json:"name"`
	Location        string             `json:"location"`
	City            string             `json:"city"`
	Price           float64            `json:"price"`
	Rating          float64            `json:"rating"`
	Description     string             `json:"description"`
	Link            string             `json:"booking_link"`
	Images          util.ImageArray    `json:"image_url"`
	RoomTypes       util.RoomTypeArray `json:"room_types"`
	RoomInfo        string             `json:"room_info"`
	Unit            string             `json:"unit"`
	TaxInfo         string             `json:"tax_info"`
	ElderlyFriendly bool               `json:"elderly_friendly"`
}

type AccommodationsSuggestion struct {
	Accommodations []AccommodationSuggestion `json:"accommodations"`
}
