package model

import (
	"time"
)

type TripDestination struct {
	TripDestinationID string     `gorm:"type:char(36);primaryKey" json:"trip_destination_id"`
	TripID            string     `gorm:"type:char(36);not null" json:"trip_id"`
	DestinationID     string     `gorm:"type:char(36);not null" json:"destination_id"`
	ArrivalDate       *time.Time `json:"arrival_date,omitempty"`
	DepartureDate     *time.Time `json:"departure_date,omitempty"`
	OrderNum          int        `gorm:"not null" json:"order_num"`

	// Associations
	// Reference to the Trip (from the same package).
	Trip        *Trip        `json:"trip,omitempty"`
	Destination *Destination `json:"destination,omitempty"`

	// Other associations as slices.
	Places         []TripPlace         `gorm:"foreignKey:TripDestinationID" json:"trip_places,omitempty"`
	Accommodations []TripAccommodation `gorm:"foreignKey:TripDestinationID" json:"trip_accommodations,omitempty"`
	Restaurants    []TripRestaurant    `gorm:"foreignKey:TripDestinationID" json:"trip_restaurants,omitempty"`
}
