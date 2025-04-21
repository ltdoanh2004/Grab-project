package model

// Accommodation represents a place for lodging at a destination.
type Accommodation struct {
	AccommodationID uint    `gorm:"primaryKey;autoIncrement" json:"accommodation_id"`
	DestinationID   uint    `json:"destination_id"`
	Name            string  `gorm:"size:100;not null" json:"name"`
	Type            string  `gorm:"type:enum('hotel','hostel','apartment','resort','other')"`
	Address         string  `json:"address"`
	BookingLink     string  `gorm:"size:100" json:"booking_link"`
	StarRating      float64 `gorm:"type:decimal(3,1)" json:"star_rating"`
	Description     string  `json:"description"`
	Amenities       string  `json:"amenities"`
	ImageURL        string  `gorm:"size:255" json:"image_url"`
}
