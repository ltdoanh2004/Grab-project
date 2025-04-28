package model

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
)

type Image struct {
	URL string `json:"url"`
	Alt string `json:"alt"`
}

type ImageArray []Image

func (ia ImageArray) Value() (driver.Value, error) {
	return json.Marshal(ia)
}

func (ia *ImageArray) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("type assertion to []byte failed")
	}
	return json.Unmarshal(bytes, ia)
}
