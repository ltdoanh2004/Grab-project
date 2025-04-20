package model

import (
	"time"
)

// TripAccommodation maps to the "trip_accommodations" table.
type TripAccommodation struct {
	TripAccommodationID uint       `gorm:"column:trip_accommodation_id;primaryKey;autoIncrement" json:"trip_accommodation_id"`
	TripID              uint       `gorm:"column:trip_id;not null" json:"trip_id"`
	AccommodationID     uint       `gorm:"column:accommodation_id;not null" json:"accommodation_id"`
	CheckInDate         *time.Time `gorm:"column:check_in_date" json:"check_in_date,omitempty"`
	CheckOutDate        *time.Time `gorm:"column:check_out_date" json:"check_out_date,omitempty"`
	Cost                float64    `gorm:"column:cost;type:decimal(10,2)" json:"cost"`
	Notes               string     `gorm:"column:notes" json:"notes"`

	// Associations
	Trip          *Trip          `json:"trip,omitempty"`
	Accommodation *Accommodation `json:"accommodation,omitempty"`
}
