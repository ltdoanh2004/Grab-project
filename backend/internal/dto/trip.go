package dto

import (
	"time"
)

type CreateTripActivityRequest struct {
	TripDestinationID string     `json:"trip_destination_id"`
	ActivityID        string     `json:"activity_id"`
	ScheduledDate     *time.Time `json:"scheduled_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	Notes             string     `json:"notes"`
}

type CreateTripAccommodationRequest struct {
	TripDestinationID string     `json:"trip_destination_id"`
	AccommodationID   string     `json:"accommodation_id"`
	CheckInDate       *time.Time `json:"check_in_date,omitempty"`
	CheckOutDate      *time.Time `json:"check_out_date,omitempty"`
	Cost              float64    `json:"cost"`
	Notes             string     `json:"notes"`
}

type CreateTripRestaurantRequest struct {
	TripDestinationID string     `json:"trip_destination_id"`
	RestaurantID      string     `json:"restaurant_id"`
	MealDate          *time.Time `json:"meal_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	ReservationInfo   string     `json:"reservation_info"`
	Notes             string     `json:"notes"`
}

type CreateTripDestinationRequest struct {
	TripID        string     `json:"trip_id"`
	DestinationID string     `json:"destination_id"`
	ArrivalDate   *time.Time `json:"arrival_date,omitempty"`
	DepartureDate *time.Time `json:"departure_date,omitempty"`
	OrderNum      int        `json:"order_num"`

	Activities     []CreateTripActivityRequest      `json:"activities,omitempty"`
	Accommodations []CreateTripAccommodationRequest `json:"accommodations,omitempty"`
	Restaurants    []CreateTripRestaurantRequest    `json:"restaurants,omitempty"`
}

type CreateTripRequest struct {
	UserID           string                         `json:"user_id"`
	TripName         string                         `json:"trip_name"`
	StartDate        time.Time                      `json:"start_date"`
	EndDate          time.Time                      `json:"end_date"`
	Budget           float64                        `json:"budget"`
	TripStatus       string                         `json:"trip_status"`
	TripDestinations []CreateTripDestinationRequest `json:"trip_destinations"`
}

type TripDTO struct {
	TripID           string               `json:"trip_id"`
	UserID           string               `json:"user_id"`
	TripName         string               `json:"trip_name"`
	StartDate        time.Time            `json:"start_date"`
	EndDate          time.Time            `json:"end_date"`
	Budget           float64              `json:"budget"`
	TripStatus       string               `json:"trip_status"`
	TripDestinations []TripDestinationDTO `json:"trip_destinations"`
}

type TripDestinationDTO struct {
	TripDestinationID string     `json:"trip_destination_id"`
	TripID            string     `json:"trip_id"`
	DestinationID     string     `json:"destination_id"`
	ArrivalDate       *time.Time `json:"arrival_date,omitempty"`
	DepartureDate     *time.Time `json:"departure_date,omitempty"`
	OrderNum          int        `json:"order_num"`

	Activities     []TripActivityDTO      `json:"activities,omitempty"`
	Accommodations []TripAccommodationDTO `json:"accommodations,omitempty"`
	Restaurants    []TripRestaurantDTO    `json:"restaurants,omitempty"`
}

type TripActivityDTO struct {
	TripActivityID    string     `json:"trip_activity_id"`
	TripDestinationID string     `json:"trip_destination_id"`
	ActivityID        string     `json:"activity_id"`
	ScheduledDate     *time.Time `json:"scheduled_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	Notes             string     `json:"notes"`
}

type TripAccommodationDTO struct {
	TripAccommodationID string     `json:"trip_accommodation_id"`
	TripDestinationID   string     `json:"trip_destination_id"`
	AccommodationID     string     `json:"accommodation_id"`
	CheckInDate         *time.Time `json:"check_in_date,omitempty"`
	CheckOutDate        *time.Time `json:"check_out_date,omitempty"`
	Cost                float64    `json:"cost"`
	Notes               string     `json:"notes"`
}

type TripRestaurantDTO struct {
	TripRestaurantID  string     `json:"trip_restaurant_id"`
	TripDestinationID string     `json:"trip_destination_id"`
	RestaurantID      string     `json:"restaurant_id"`
	MealDate          *time.Time `json:"meal_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	ReservationInfo   string     `json:"reservation_info"`
	Notes             string     `json:"notes"`
}
