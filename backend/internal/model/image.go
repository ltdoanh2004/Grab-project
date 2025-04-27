package model

type Image struct {
	ImageID         string `gorm:"type:char(36);primaryKey" json:"image_id"`
	AccommodationID string `gorm:"type:char(36);not null;uniqueIndex:idx_accommodation_image" json:"accommodation_id"`
	Url             string `gorm:"size:255;not null" json:"url"`
	Alt             string `gorm:"size:255;not null" json:"alt"`

	Accommodation *Accommodation `gorm:"foreignKey:AccommodationID" json:"accommodation,omitempty"`
}
