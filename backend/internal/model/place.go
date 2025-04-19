package model

// Place maps to the "places" table.
type Place struct {
	PlaceID          uint    `gorm:"column:place_id;primaryKey;autoIncrement" json:"place_id"`
	DestinationID    uint    `gorm:"column:destination_id" json:"destination_id"`
	Name             string  `gorm:"column:name;size:100;not null" json:"name"`
	PlaceType        string  `gorm:"column:place_type;size:50" json:"place_type"`
	Description      string  `gorm:"column:description" json:"description"`
	Address          string  `gorm:"column:address" json:"address"`
	EntranceFee      float64 `gorm:"column:entrance_fee;type:decimal(10,2)" json:"entrance_fee"`
	AvgVisitDuration int     `gorm:"column:avg_visit_duration" json:"avg_visit_duration"`
	OpeningHours     string  `gorm:"column:opening_hours" json:"opening_hours"`
	PopularityScore  float64 `gorm:"column:popularity_score;type:decimal(3,1)" json:"popularity_score"`
	ImageURL         string  `gorm:"column:image_url;size:255" json:"image_url"`
}
