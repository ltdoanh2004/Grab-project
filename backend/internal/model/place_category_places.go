package model

type PlaceCategoryPlace struct {
	PlaceID    string `gorm:"type:char(36);primaryKey;column:place_id" json:"place_id"`
	CategoryID string `gorm:"type:char(36);primaryKey;column:category_id" json:"category_id"`
}
