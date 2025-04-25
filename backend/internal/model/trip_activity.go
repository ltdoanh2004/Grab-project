package model

import "time"

// TripActivity associates an activity with a trip.
type TripActivity struct {
	TripActivityID    string     `gorm:"type:char(36);primaryKey" json:"trip_activity_id"`
	TripDestinationID string     `gorm:"type:char(36);not null" json:"trip_destination_id"`
	ActivityID        string     `gorm:"type:char(36);not null" json:"activity_id"`
	ScheduledDate     *time.Time `json:"scheduled_date,omitempty"`
	StartTime         *time.Time `gorm:"column:start_time" json:"start_time,omitempty"`
	EndTime           *time.Time `gorm:"column:end_time" json:"end_time,omitempty"`
	Notes             string     `json:"notes"`

	// Associations
	TripDestination *TripDestination `json:"trip_destination,omitempty"`
	Activity        *Activity        `gorm:"foreignKey:ActivityID" json:"activity,omitempty"`
	Place           *Place           `gorm:"foreignKey:PlaceID" json:"place,omitempty"`
}
