package dto

type CreateRoomTypeDTO struct {
	Name       string `json:"name"`
	BedType    string `json:"bed_type"`
	Price      string `json:"price"`
	Taxes      string `json:"taxes_and_fees"`
	Occupancy  string `json:"occupancy"`
	Conditions string `json:"conditions"`
}
