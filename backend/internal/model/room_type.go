package model

type RoomType struct {
	RoomTypeID      string `gorm:"type:char(36);primaryKey" json:"room_type_id"`
	AccommodationID string `gorm:"type:char(36)" json:"accommodation_id"`
	Name            string `gorm:"size:255;not null" json:"name"`
	BedType         string `gorm:"size:255;not null" json:"bed_type"`
	Price           string `gorm:"size:255;not null" json:"price"`
	TaxesAndFees    string `gorm:"size:255;not null" json:"taxes_and_fees"`
	Occupancy       string `gorm:"size:255;not null" json:"occupancy"`
	Conditions      string `gorm:"type:text;not null" json:"conditions"`

	Accommodation *Accommodation `json:"accommodation"`
}
