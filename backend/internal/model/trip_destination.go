package model

import (
	"time"
)

// TripDestination links a trip with a destination.
type TripDestination struct {
	TripDestinationID string     `gorm:"type:char(36);primaryKey" json:"trip_destination_id"`
	TripID            string     `gorm:"type:char(36);not null" json:"trip_id"`
	DestinationID     string     `gorm:"type:char(36);not null" json:"destination_id"`
	ArrivalDate       *time.Time `json:"arrival_date,omitempty"`
	DepartureDate     *time.Time `json:"departure_date,omitempty"`
	OrderNum          int        `gorm:"not null" json:"order_num"`

	// Associations
	// Reference to the Trip (from the same package).
	Trip *Trip `json:"trip,omitempty"`
	// Reference to a destination (from the destination package).
	Destination *Destination `gorm:"foreignKey:DestinationID" json:"destination,omitempty"`

	// Other associations as slices.
	Activities     []TripActivity      `gorm:"foreignKey:TripDestinationID" json:"activities,omitempty"`
	Accommodations []TripAccommodation `gorm:"foreignKey:TripDestinationID" json:"accommodations,omitempty"`
	Restaurants    []TripRestaurant    `gorm:"foreignKey:TripDestinationID" json:"restaurants,omitempty"`
}
