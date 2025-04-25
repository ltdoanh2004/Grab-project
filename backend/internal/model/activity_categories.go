package model

type ActivityCategory struct {
	CategoryID   string `gorm:"type:char(36);primaryKey" json:"category_id"`
	CategoryName string `gorm:"size:50;not null" json:"category_name"`
	Description  string `json:"description"`

	Activities []Activity `gorm:"foreignKey:CategoryID" json:"activities,omitempty"`
}
