package model

import (
	"time"
)

// TripAccommodation maps to the "trip_accommodations" table.
type TripAccommodation struct {
	TripAccommodationID string     `gorm:"type:char(36);primaryKey" json:"trip_accommodation_id"`
	TripDestinationID   string     `gorm:"type:char(36);column:trip_destination_id;not null" json:"trip_destination_id"`
	AccommodationID     string     `gorm:"type:char(36);column:accommodation_id;not null" json:"accommodation_id"`
	CheckInDate         *time.Time `gorm:"column:check_in_date" json:"check_in_date,omitempty"`
	CheckOutDate        *time.Time `gorm:"column:check_out_date" json:"check_out_date,omitempty"`
	StartTime           *time.Time `gorm:"column:start_time" json:"start_time,omitempty"`
	EndTime             *time.Time `gorm:"column:end_time" json:"end_time,omitempty"`
	Cost                float64    `gorm:"column:cost;type:decimal(10,2)" json:"cost"`
	Notes               string     `gorm:"column:notes" json:"notes"`

	// Associations
	TripDestination *TripDestination `json:"trip_destination,omitempty"`
	Accommodation   *Accommodation   `json:"accommodation,omitempty"`
	Comments        []Comment        `gorm:"foreignKey:TripAccommodationID" json:"comments,omitempty"`
}
