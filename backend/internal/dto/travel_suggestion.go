package dto

import (
	"skeleton-internship-backend/internal/model"
	"time"
)

type Participant struct {
	Adult    int `json:"adult"`
	Children int `json:"children"`
	Infant   int `json:"ifant"`
	Pet      int `json:"pet"`
}
type TravelPreference struct {
	Location    string            `json:"location"`
	Participant Participant       `json:"participant"`
	Budget      string            `json:"budget"`
	StartDate   time.Time         `json:"start_date"`
	EndDate     time.Time         `json:"end_date"`
	Options     model.StringArray `json:"options"`
}

type TravelSuggestionResponse struct {
	IDs model.StringArray `json:"ids"`
}

type PlaceSuggestion struct {
	PlaceID       string            `json:"place_id"`
	DestinationID string            `json:"destination_id"`
	Name          string            `json:"name"`
	URL           string            `json:"url"`
	Address       string            `json:"address"`
	Duration      string            `json:"duration"`
	Type          string            `json:"type"`
	Images        model.ImageArray  `json:"images"`
	MainImage     string            `json:"main_image"`
	Price         float64           `json:"price"`
	Rating        float64           `json:"rating"`
	Description   string            `json:"description"`
	OpeningHours  string            `json:"opening_hours"`
	Reviews       model.StringArray `json:"reviews"`
	Categories    string            `json:"categories"`
	Unit          string            `json:"unit"`
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

type SuggestWithIDAndType struct {
	Name string `json:"name"`
	Type string `json:"type"`
	Args string `json:"args"`
	ID   string `json:"id"`
}
