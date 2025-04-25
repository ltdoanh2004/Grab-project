package model

type Activity struct {
	ActivityID    string  `gorm:"type:char(36);primaryKey" json:"activity_id"`
	DestinationID string  `gorm:"type:char(36)" json:"destination_id"`
	CategoryID    string  `gorm:"type:char(36)" json:"category_id"`
	Name          string  `gorm:"size:100;not null" json:"name"`
	Description   string  `json:"description"`
	Duration      int     `json:"duration"`
	Cost          float64 `gorm:"type:decimal(10,2)" json:"cost"`
	ImageURL      string  `gorm:"size:255" json:"image_url"`
	PlaceID       string  `gorm:"type:char(36)" json:"place_id"`

	Place            *Place            `json:"place,omitempty"`
	ActivityCategory *ActivityCategory `gorm:"foreignKey:CategoryID" json:"activity_category,omitempty"`
	Destination      *Destination      `json:"destination,omitempty"`
}
