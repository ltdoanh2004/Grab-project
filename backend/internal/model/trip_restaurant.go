package model

import (
	"time"
)

// TripRestaurant maps to the "trip_restaurants" table.
type TripRestaurant struct {
	TripRestaurantID uint       `gorm:"column:trip_restaurant_id;primaryKey;autoIncrement" json:"trip_restaurant_id"`
	TripID           uint       `gorm:"column:trip_id;not null" json:"trip_id"`
	RestaurantID     uint       `gorm:"column:restaurant_id;not null" json:"restaurant_id"`
	MealDate         *time.Time `gorm:"column:meal_date" json:"meal_date,omitempty"`
	MealTime         *time.Time `gorm:"column:meal_time" json:"meal_time,omitempty"`
	ReservationInfo  string     `gorm:"column:reservation_info;size:255" json:"reservation_info"`
	Notes            string     `gorm:"column:notes" json:"notes"`

	// Associations: Each TripRestaurant is linked to a Trip (from this package) and a Restaurant from the destination package.
	Trip       *Trip       `json:"trip,omitempty"`
	Restaurant *Restaurant `gorm:"foreignKey:RestaurantID" json:"restaurant,omitempty"`
}
