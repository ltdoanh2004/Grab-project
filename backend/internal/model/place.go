package model

type Place struct {
	PlaceID       string      `gorm:"type:char(36);primaryKey" json:"place_id"`
	DestinationID string      `gorm:"type:char(36)" json:"destination_id"`
	Name          string      `gorm:"not null" json:"name"`
	URL           string      `gorm:"size:255" json:"url"`
	Address       string      `gorm:"size:255" json:"address"`
	Duration      string      `gorm:"size:50" json:"duration"`
	Type          string      `json:"type"`
	Categories    string      `json:"categories"`
	Images        ImageArray  `gorm:"type:json" json:"images"`
	MainImage     string      `gorm:"size:255" json:"main_image"`
	Price         float64     `gorm:"size:20" json:"price"`
	Rating        float64     `json:"rating"`
	Description   string      `gorm:"type:text" json:"description"`
	OpeningHours  string      `gorm:"type:text" json:"opening_hours"`
	Reviews       StringArray `gorms:"type:json" json:"reviews"`
	Unit          string      `gorm:"size:50" json:"unit"`
}
