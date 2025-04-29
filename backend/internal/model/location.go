package model

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
)

// Location represents the nested location details.
type Location struct {
	Lat float64 `json:"lat"`
	Lon float64 `json:"lon"`
}

func (l Location) Value() (driver.Value, error) {
	return json.Marshal(l)
}

func (l *Location) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("type assertion to []byte failed")
	}
	return json.Unmarshal(bytes, l)
}
