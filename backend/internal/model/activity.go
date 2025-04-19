package model

// Activity represents an available activity at a destination.
type Activity struct {
	ActivityID    uint    `gorm:"primaryKey;autoIncrement" json:"activity_id"`
	DestinationID uint    `json:"destination_id"`
	CategoryID    uint    `json:"category_id"`
	Name          string  `gorm:"size:100;not null" json:"name"`
	Description   string  `json:"description"`
	Duration      int     `json:"duration"` // Duration in minutes
	Cost          float64 `gorm:"type:decimal(10,2)" json:"cost"`
	ImageURL      string  `gorm:"size:255" json:"image_url"`

	// Association: Activity belongs to a Destination.
	// Note: if you need this relation in activity, import the same package,
	// or simply store the DestinationID for lightweight operations.
}
