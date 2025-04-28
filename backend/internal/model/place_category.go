package model

type PlaceCategory struct {
	CategoryID   string `gorm:"type:char(36);primaryKey" json:"category_id"`
	CategoryName string `gorm:"size:50;not null" json:"category_name"`
	Description  string `json:"description"`

	Places []Place `gorm:"many2many:place_category_places;joinForeignKey:category_id;JoinReferences:place_id" json:"places,omitempty"`
}
