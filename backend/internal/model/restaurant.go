package model

// Restaurant maps to the "restaurants" table.
type Restaurant struct {
	RestaurantID  string       `gorm:"type:char(36);primaryKey" json:"restaurant_id"`
	DestinationID string       `gorm:"type:char(36);" json:"destination_id"`
	Name          string       `json:"name"`
	Address       string       `json:"address"`
	Rating        float64      `json:"rating"`
	Phone         string       `json:"phone"`
	PhotoURL      string       `json:"photo_url"`
	URL           string       `json:"url"`
	Location      Location     `gorm:"type:json" json:"location"`
	Reviews       StringArray  `gorm:"type:json" json:"reviews"`
	Services      ServiceArray `gorm:"type:json" json:"services"`
	IsDelivery    bool         `json:"is_delivery"`
	IsBooking     bool         `json:"is_booking"`
	IsOpening     bool         `json:"is_opening"`
	PriceRange    PriceRange   `gorm:"type:json" json:"price_range"`
	Description   string       `json:"description"`
	Cuisines      string       `json:"cuisines"`
	OpeningHours  string       `json:"opening_hours"`
}
