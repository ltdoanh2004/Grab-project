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
	if len(ia) == 0 {
		return "[]", nil
	}
	bytes, err := json.Marshal(ia)
	if err != nil {
		return nil, err
	}
	return string(bytes), nil
}

func (ia *ImageArray) Scan(value interface{}) error {
	if value == nil {
		*ia = ImageArray{}
		return nil
	}

	switch v := value.(type) {
	case []byte:
		return json.Unmarshal(v, ia)
	case string:
		return json.Unmarshal([]byte(v), ia)
	default:
		return errors.New("invalid type for ImageArray")
	}
}
