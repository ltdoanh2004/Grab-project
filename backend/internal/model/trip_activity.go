package model

import "time"

// TripActivity associates an activity with a trip.
type TripActivity struct {
	TripActivityID string     `gorm:"type:char(36);primaryKey" json:"trip_activity_id"`
	TripID         uint       `gorm:"not null" json:"trip_id"`
	ActivityID     uint       `gorm:"not null" json:"activity_id"`
	ScheduledDate  *time.Time `json:"scheduled_date,omitempty"`
	StartTime      *string    `json:"start_time,omitempty"` // Can be changed to time.Time if needed.
	EndTime        *string    `json:"end_time,omitempty"`
	Notes          string     `json:"notes"`

	// Associations
	Trip     *Trip     `json:"trip,omitempty"`
	Activity *Activity `gorm:"foreignKey:ActivityID" json:"activity,omitempty"`
}
