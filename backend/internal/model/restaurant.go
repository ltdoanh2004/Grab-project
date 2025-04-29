package model

// Restaurant maps to the "restaurants" table.
type Restaurant struct {
	RestaurantID   string      `gorm:"type:char(36);primaryKey" json:"restaurant_id"`
	DestinationID  string      `gorm:"type:char(36);" json:"destination_id"`
	Name           string      `json:"name"`
	Address        string      `json:"address"`
	Rating         float64     `json:"rating"`
	Phone          string      `json:"phone"`
	PhotoURL       string      `json:"photo_url"`
	URL            string      `json:"url"`
	Location       Location    `json:"location"`
	Reviews        StringArray `gorm:"type:json" json:"reviews"`
	Services       StringArray `gorm:"type:json" json:"services"`
	IsDelivery     bool        `json:"is_delivery"`
	IsBooking      bool        `json:"is_booking"`
	IsOpening      bool        `json:"is_opening"`
	PriceRange     string      `json:"price_range"`
	Description    string      `json:"description"`
	Cuisines       string      `json:"cuisines"`
	NumReviews     int         `json:"num_reviews"`
	ExampleReviews string      `json:"example_reviews"`
	MediaURLs      string      `json:"media_urls"`
	MainImage      string      `json:"main_image"`
	OpeningHours   string      `json:"opening_hours"`
	ReviewSummary  string      `json:"review_summary"`
}
