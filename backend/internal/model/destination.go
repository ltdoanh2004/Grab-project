package model

type Destination struct {
	DestinationID string `gorm:"type:char(36);primaryKey" json:"destination_id"`
	Name          string `gorm:"size:100;not null" json:"name"`
	City          string `gorm:"size:100" json:"city"`
	Description   string `json:"description"`
	Climate       string `gorm:"size:50" json:"climate"`
	BestSeason    string `gorm:"size:100" json:"best_season"`
	ImageURL      string `gorm:"size:255" json:"image_url"`

	Activities     []Activity      `gorm:"foreignKey:DestinationID" json:"activities,omitempty"`
	Places         []Place         `gorm:"foreignKey:DestinationID" json:"places,omitempty"`
	Accommodations []Accommodation `gorm:"foreignKey:DestinationID" json:"accommodations,omitempty"`
	Restaurants    []Restaurant    `gorm:"foreignKey:DestinationID" json:"restaurants,omitempty"`
}
