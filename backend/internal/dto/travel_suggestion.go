package dto

import (
	"skeleton-internship-backend/internal/model"
)

type TravelPreference struct {
	Location     string            `json:"location"`
	TravelStyle  string            `json:"travel_style"`
	Places       model.StringArray `json:"places"`
	Budget       string            `json:"budget"`
	DurationDays int               `json:"duration_days"`
	Season       string            `json:"season"`
	Limit        int               `json:"limit"`
}

type TravelSuggestionResponse struct {
	IDs model.StringArray `json:"ids"`
}

type PlaceSuggestion struct {
	PlaceID       string            `gorm:"type:char(36);primaryKey" json:"place_id"`
	DestinationID string            `gorm:"type:char(36)" json:"destination_id"`
	Name          string            `gorm:"size:100;not null" json:"name"`
	URL           string            `gorm:"size:255" json:"url"`
	Address       string            `gorm:"size:255" json:"address"`
	Duration      string            `gorm:"size:50" json:"duration"`
	Type          string            `gorm:"size:50" json:"type"`
	Images        model.ImageArray  `gorm:"type:json" json:"images"`
	MainImage     string            `gorm:"size:255" json:"main_image"`
	Price         string            `gorm:"size:20" json:"price"`
	Rating        float64           `json:"rating"`
	Description   string            `gorm:"type:text" json:"description"`
	OpeningHours  string            `gorm:"type:text" json:"opening_hours"`
	Reviews       model.StringArray `gorm:"type:json" json:"reviews"`
	Categories    string            `gorm:"type:json" json:"categories"`
}
type PlacesSuggestion struct {
	Places []PlaceSuggestion `json:"places"`
}

type RestaurantSuggestion struct {
	RestaurantID  string             `json:"restaurant_id"`
	DestinationID string             `json:"destination_id"`
	Name          string             `json:"name"`
	Address       string             `json:"address"`
	Rating        float64            `json:"rating"`
	Phone         string             `json:"phone"`
	PhotoURL      string             `json:"photo_url"`
	URL           string             `json:"url"`
	Location      model.Location     `json:"location"`
	Reviews       model.StringArray  `json:"reviews"`
	Services      model.ServiceArray `json:"services"`
	IsDelivery    bool               `json:"is_delivery"`
	IsBooking     bool               `json:"is_booking"`
	IsOpening     bool               `json:"is_opening"`
	PriceRange    model.PriceRange   `json:"price_range"`
	Description   string             `json:"description"`
	Cuisines      string             `json:"cuisines"`
	OpeningHours  string             `json:"opening_hours"`
}

type RestaurantsSuggestion struct {
	Restaurants []RestaurantSuggestion `json:"restaurants"`
}

type AccommodationSuggestion struct {
	AccommodationID string              `json:"accommodation_id"`
	DestinationID   string              `json:"destination_id"`
	Name            string              `json:"name"`
	Location        string              `json:"location"`
	City            string              `json:"city"`
	Price           float64             `json:"price"`
	Rating          float64             `json:"rating"`
	Description     string              `json:"description"`
	Link            string              `json:"booking_link"`
	Images          model.ImageArray    `json:"image_url"`
	RoomTypes       model.RoomTypeArray `json:"room_types"`
	RoomInfo        string              `json:"room_info"`
	Unit            string              `json:"unit"`
	TaxInfo         string              `json:"tax_info"`
	ElderlyFriendly bool                `json:"elderly_friendly"`
}

type AccommodationsSuggestion struct {
	Accommodations []AccommodationSuggestion `json:"accommodations"`
}

type TripSuggestionRequest struct {
	Accommodation AccommodationsSuggestion `json:"accommodation"`
	Places        PlacesSuggestion         `json:"places"`
	Restaurants   RestaurantsSuggestion    `json:"restaurants"`
}
