package dto

import (
	"time"
)

type CreateTripDestinationRequest struct {
	TripID           string     `json:"trip_id"`
	DestinationID    string     `json:"destination_id"`
	ArrivalDate      *time.Time `json:"arrival_date"`
	DepartureDate    *time.Time `json:"departure_date"`
	OrderNum         int        `json:"order_num"`
	AccommodationIDs []string   `json:"accommodation_ids"`
	ActivitiyIDs     []string   `json:"activity_ids"`
	RestaurantIDs    []string   `json:"restaurant_ids"`
}

type CreateTripDestinationResponse struct {
	TripDestinationID string `json:"trip_destination_id"`
}

type GetTripDestinationResponse struct {
	TripDestinationID string     `json:"trip_destination_id"`
	TripID            string     `json:"trip_id"`
	DestinationID     string     `json:"destination_id"`
	ArrivalDate       *time.Time `json:"arrival_date"`
	DepartureDate     *time.Time `json:"departure_date"`
	OrderNum          int        `json:"order_num"`
	AccommodationIDs  []string   `json:"accommodation_ids"`
	ActivitiyIDs      []string   `json:"activity_ids"`
	RestaurantIDs     []string   `json:"restaurant_ids"`
}
