package dto

import (
	"skeleton-internship-backend/internal/model"
	"time"
)

type CreateTripRequest struct {
	UserID           string                  `json:"user_id"`
	TripName         string                  `json:"trip_name"`
	StartDate        time.Time               `json:"start_date"`
	EndDate          time.Time               `json:"end_date"`
	Budget           float64                 `json:"budget"`
	TripDestinations []model.TripDestination `json:"trip_destinations"`
}

type CreateTripResponse struct {
	TripID string `json:"trip_id"`
}

type GetTripResponse struct {
	TripID           string                  `json:"trip_id"`
	UserID           string                  `json:"user_id"`
	TripName         string                  `json:"trip_name"`
	StartDate        time.Time               `json:"start_date"`
	EndDate          time.Time               `json:"end_date"`
	Budget           float64                 `json:"budget"`
	TripDestinations []model.TripDestination `json:"trip_destinations"`
}
