package model

// ActivityCategory maps to the "activity_categories" table.
type ActivityCategory struct {
	CategoryID   string `gorm:"type:char(36);column:category_id;primaryKey" json:"category_id"`
	CategoryName string `gorm:"column:category_name;size:50;not null" json:"category_name"`
	Description  string `gorm:"column:description" json:"description"`
}
