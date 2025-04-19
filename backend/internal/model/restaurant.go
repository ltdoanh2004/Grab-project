package model

// Restaurant maps to the "restaurants" table.
type Restaurant struct {
	RestaurantID      uint    `gorm:"column:restaurant_id;primaryKey;autoIncrement" json:"restaurant_id"`
	DestinationID     uint    `gorm:"column:destination_id" json:"destination_id"` // FK referencing destinations table
	Name              string  `gorm:"column:name;size:100;not null" json:"name"`
	EstablishmentType string  `gorm:"column:establishment_type;size:50" json:"establishment_type"`
	CuisineType       string  `gorm:"column:cuisine_type;size:100" json:"cuisine_type"`
	Description       string  `gorm:"column:description" json:"description"`
	Address           string  `gorm:"column:address" json:"address"`
	PriceRange        string  `gorm:"column:price_range;type:enum('$','$$','$$$','$$$$','$$$$$')" json:"price_range"`
	AvgRating         float64 `gorm:"column:avg_rating;type:decimal(3,1)" json:"avg_rating"`
	OpeningHours      string  `gorm:"column:opening_hours" json:"opening_hours"`
	ImageURL          string  `gorm:"column:image_url;size:255" json:"image_url"`
}
