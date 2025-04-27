package model

type Image struct {
	ImageID         string `gorm:"type:char(36);primaryKey" json:"image_id"`
	AccommodationID string `gorm:"type:char(36)" json:"accommodation_id"`
	Url             string `gorm:"size:255;not null" json:"url"`
	Alt             string `gorm:"size:255;not null" json:"alt"`

	Accommodation *Accommodation `json:"accommodation,omitempty"`
}
