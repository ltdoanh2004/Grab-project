package model

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
)

type RoomType struct {
	URL string `json:"url"`
	Alt string `json:"alt"`
}

type RoomTypeArray []RoomType

func (rta *RoomTypeArray) Value() (driver.Value, error) {
	return json.Marshal(rta)
}

func (rta *RoomTypeArray) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("type assertion to []byte failed")
	}
	return json.Unmarshal(bytes, rta)
}
