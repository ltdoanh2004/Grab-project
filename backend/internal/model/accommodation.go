package model

// Accommodation represents a place for lodging at a destination.
type Accommodation struct {
	AccommodationID string        `gorm:"type:char(36);primaryKey" json:"accommodation_id"`
	DestinationID   string        `gorm:"type:char(36);" json:"destination_id"`
	Name            string        `gorm:"size:100;not null" json:"name"`
	Link            string        `json:"link"`
	Price           float64       `gorm:"type:decimal(10,2)" json:"price"`
	TaxInfo         string        `json:"tax_info"`
	Rating          float64       `gorm:"type:decimal(3,1)" json:"rating"`
	Location        string        `json:"location"`
	Description     string        `json:"description"`
	City            string        `json:"city"`
	ElderlyFriendly bool          `json:"elderly_friendly"`
	RoomInfo        string        `json:"room_info"`
	Unit            string        `json:"unit"`
	Images          ImageArray    `gorm:"type:json" json:"images"`
	RoomTypes       RoomTypeArray `json:"room_types"`
}
