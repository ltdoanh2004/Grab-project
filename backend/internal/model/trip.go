package model

import (
	"time"
)

// Trip represents travel plans created by a user.
type Trip struct {
	TripID     uint      `gorm:"primaryKey;autoIncrement" json:"trip_id"`
	UserID     uint      `gorm:"not null" json:"user_id"`
	TripName   string    `gorm:"size:100;not null" json:"trip_name"`
	StartDate  time.Time `gorm:"not null" json:"start_date"`
	EndDate    time.Time `gorm:"not null" json:"end_date"`
	Budget     float64   `gorm:"type:decimal(10,2)" json:"budget"`
	TripStatus string    `gorm:"type:enum('planning','confirmed','completed','canceled');default:'planning'" json:"trip_status"`
	CreatedAt  time.Time `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt  time.Time `gorm:"autoUpdateTime" json:"updated_at"`

	// Associations
	// Each trip is created by a user.
	User User `gorm: json:"user,omitempty"`

	// Other associations as slices.
	Destinations   []TripDestination   `gorm:"foreignKey:TripID" json:"destinations,omitempty"`
	Activities     []TripActivity      `gorm:"foreignKey:TripID" json:"activities,omitempty"`
	Accommodations []TripAccommodation `gorm:"foreignKey:TripID" json:"accommodations,omitempty"`
	Places         []TripPlace         `gorm:"foreignKey:TripID" json:"places,omitempty"`
	Restaurants    []TripRestaurant    `gorm:"foreignKey:TripID" json:"restaurants,omitempty"`
}
