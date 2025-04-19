package model

import (
	"time"
)

// TripPlace maps to the "trip_places" table.
type TripPlace struct {
	TripPlaceID    uint       `gorm:"column:trip_place_id;primaryKey;autoIncrement" json:"trip_place_id"`
	TripID         uint       `gorm:"column:trip_id;not null" json:"trip_id"`
	PlaceID        uint       `gorm:"column:place_id;not null" json:"place_id"`
	VisitDate      *time.Time `gorm:"column:visit_date" json:"visit_date,omitempty"`
	VisitStartTime *string    `gorm:"column:visit_start_time" json:"visit_start_time,omitempty"`
	VisitEndTime   *string    `gorm:"column:visit_end_time" json:"visit_end_time,omitempty"`
	Notes          string     `gorm:"column:notes" json:"notes"`

	// Associations
	Trip  *Trip  `gorm:"foreignKey:TripID;constraint:OnDelete:CASCADE" json:"trip,omitempty"`
	Place *Place `gorm:"foreignKey:PlaceID" json:"place,omitempty"`
}
