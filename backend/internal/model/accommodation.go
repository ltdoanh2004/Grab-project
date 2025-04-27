package model

// Accommodation represents a place for lodging at a destination.
type Accommodation struct {
	AccommodationID string  `gorm:"type:char(36);primaryKey" json:"accommodation_id"`
	DestinationID   string  `gorm:"type:char(36);" json:"destination_id"`
	Name            string  `gorm:"size:100;not null" json:"name"`
	Link            string  `gorm:"size:255" json:"link"`
	Price           float64 `gorm:"type:decimal(10,2)" json:"price"`
	TaxInfo         string  `json:"tax_info"`
	Rating          float64 `gorm:"type:decimal(3,1)" json:"rating"`
	Location        string  `json:"location"`
	Description     string  `json:"description"`
	City            string  `json:"city"`
	ElderlyFriendly bool    `json:"elderly_friendly"`
	RoomInfo        string  `json:"room_info"`
	Unit            string  `json:"unit"`

	// Update relationship definitions
	Images    []Image    `gorm:"foreignKey:AccommodationID" json:"images"`
	RoomTypes []RoomType `gorm:"foreignKey:AccommodationID" json:"room_types"`
}
