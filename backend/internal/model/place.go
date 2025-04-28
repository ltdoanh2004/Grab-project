package model

import "skeleton-internship-backend/internal/util"

type Place struct {
	PlaceID       string           `gorm:"type:char(36);primaryKey" json:"place_id"`
	DestinationID string           `gorm:"type:char(36)" json:"destination_id"`
	Name          string           `gorm:"size:100;not null" json:"name"`
	URL           string           `gorm:"size:255" json:"url"`
	Address       string           `gorm:"size:255" json:"address"`
	Duration      string           `gorm:"size:50" json:"duration"`
	Type          string           `gorm:"size:50" json:"type"`
	ImageURLs     util.StringArray `gorm:"type:json" json:"image_urls"`
	MainImage     string           `gorm:"size:255" json:"main_image"`
	Price         string           `gorm:"size:20" json:"price"`
	Rating        float64          `json:"rating"`
	Description   string           `gorm:"type:text" json:"description"`
	OpeningHours  string           `gorm:"type:text" json:"opening_hours"`
	Reviews       util.StringArray `gorm:"type:json" json:"reviews"`

	Categories []PlaceCategory `gorm:"many2many:place_category_places;joinForeignKey:place_id;JoinReferences:category_id" json:"categories"`
}
