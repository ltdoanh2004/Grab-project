package model

import (
	"time"
)

// Trip represents travel plans created by a user.
type Trip struct {
	TripID     string    `gorm:"type:char(36);primaryKey" json:"trip_id"`
	UserID     string    `gorm:"type:char(36);not null" json:"user_id"`
	TripName   string    `gorm:"not null" json:"trip_name"`
	StartDate  time.Time `gorm:"not null" json:"start_date"`
	EndDate    time.Time `gorm:"not null" json:"end_date"`
	Budget     float64   `gorm:"type:decimal(10,2)" json:"budget"`
	TripStatus string    `gorm:"type:enum('planning','confirmed','completed','canceled');default:'planning'" json:"trip_status"`
	CreatedAt  time.Time `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt  time.Time `gorm:"autoUpdateTime" json:"updated_at"`

	// Associations
	User             *User             `json:"user,omitempty"`
	TripDestinations []TripDestination `gorm:"foreignKey:TripID" json:"trip_destinations,omitempty"`

	// New association with TravelPreference (one-to-one)
	TravelPreference *TravelPreference `gorm:"foreignKey:TripID" json:"travel_preference,omitempty"`
}
