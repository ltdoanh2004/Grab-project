package model

// Activity represents an available activity at a destination.
type Activity struct {
	ActivityID    string  `gorm:"type:char(36);primaryKey" json:"activity_id"`
	DestinationID uint    `json:"destination_id"`
	CategoryID    uint    `json:"category_id"`
	Name          string  `gorm:"size:100;not null" json:"name"`
	Description   string  `json:"description"`
	Duration      int     `json:"duration"` // Duration in minutes
	Cost          float64 `gorm:"type:decimal(10,2)" json:"cost"`
	ImageURL      string  `gorm:"size:255" json:"image_url"`

	ActivityCategory ActivityCategory `gorm:"foreignKey:CategoryID" json:"activity,omitempty"`
}
