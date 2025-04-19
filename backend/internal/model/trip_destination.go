package model

import (
	"time"
)

// TripDestination links a trip with a destination.
type TripDestination struct {
	TripDestinationID uint       `gorm:"primaryKey;autoIncrement" json:"trip_destination_id"`
	TripID            uint       `gorm:"not null" json:"trip_id"`
	DestinationID     uint       `gorm:"not null" json:"destination_id"`
	ArrivalDate       *time.Time `json:"arrival_date,omitempty"`
	DepartureDate     *time.Time `json:"departure_date,omitempty"`
	OrderNum          int        `gorm:"not null" json:"order_num"`

	// Associations
	// Reference to the Trip (from the same package).
	Trip *Trip `gorm:"foreignKey:TripID;constraint:OnDelete:CASCADE" json:"trip,omitempty"`
	// Reference to a destination (from the destination package).
	Destination *Destination `gorm:"foreignKey:DestinationID" json:"destination,omitempty"`
}
