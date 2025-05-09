package model

import "time"

// TripPlace associates an place with a trip.
type TripPlace struct {
	TripPlaceID       string     `gorm:"type:char(36);primaryKey" json:"trip_place_id"`
	TripDestinationID string     `gorm:"type:char(36);not null" json:"trip_destination_id"`
	PlaceID           string     `gorm:"type:char(36);not null" json:"place_id"`
	ScheduledDate     *time.Time `json:"scheduled_date,omitempty"`
	StartTime         *time.Time `gorm:"column:start_time" json:"start_time,omitempty"`
	EndTime           *time.Time `gorm:"column:end_time" json:"end_time,omitempty"`
	Notes             string     `json:"notes"`
	PriceAIEstimate   float64    `gorm:"column:price_ai_estimate" json:"price_ai_estimate"`

	// Update associations
	TripDestination *TripDestination `json:"trip_destination,omitempty"`
	Place           *Place           `json:"place,omitempty"`
	Comments        []Comment        `gorm:"foreignKey:TripPlaceID" json:"comments,omitempty"`
}
