package model

type RoomType struct {
	RoomTypeID      string `gorm:"type:char(36);primaryKey" json:"room_type_id"`
	AccommodationID string `gorm:"type:char(36);not null;uniqueIndex:idx_accommodation_room" json:"accommodation_id"`
	Name            string `gorm:"size:255;not null" json:"name"`
	BedType         string `gorm:"size:255;not null" json:"bed_type"`
	Price           string `gorm:"size:255;not null" json:"price"`
	TaxesAndFees    string `gorm:"size:255;not null" json:"taxes_and_fees"`
	Occupancy       string `gorm:"size:255;not null" json:"occupancy"`
	Conditions      string `gorm:"type:text;not null" json:"conditions"`

	Accommodation *Accommodation `gorm:"constraint:OnUpdate:CASCADE,OnDelete:CASCADE;foreignKey:AccommodationID;references:AccommodationID" json:"-"`
}
