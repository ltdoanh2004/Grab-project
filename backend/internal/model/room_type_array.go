package model

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
)

type RoomType struct {
	Name       string `json:"name"`
	BedType    string `json:"bed_type"`
	Price      string `json:"price"`
	TaxAndFee  string `json:"tax_and_fee"`
	Occupancy  string `json:"occupancy"`
	Conditions string `json:"conditions"`
}

type RoomTypeArray []RoomType

func (rta RoomTypeArray) Value() (driver.Value, error) {
	if len(rta) == 0 {
		return "[]", nil
	}
	bytes, err := json.Marshal(rta)
	if err != nil {
		return nil, err
	}
	return string(bytes), nil
}

func (rta *RoomTypeArray) Scan(value interface{}) error {
	if value == nil {
		*rta = RoomTypeArray{}
		return nil
	}

	switch v := value.(type) {
	case []byte:
		return json.Unmarshal(v, rta)
	case string:
		return json.Unmarshal([]byte(v), rta)
	default:
		return errors.New("invalid type for RoomTypeArray")
	}
}
