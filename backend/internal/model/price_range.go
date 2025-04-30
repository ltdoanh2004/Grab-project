package model

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
)

// PriceRange represents a range with a minimum and maximum price.
type PriceRange struct {
	MinPrice int `json:"min_price"`
	MaxPrice int `json:"max_price"`
}

// Value converts the PriceRange struct to a JSON-encoded string.
func (pr PriceRange) Value() (driver.Value, error) {
	return json.Marshal(pr)
}

// Scan parses a JSON-encoded value into the PriceRange struct.
func (pr *PriceRange) Scan(src interface{}) error {
	var source []byte

	switch v := src.(type) {
	case string:
		source = []byte(v)
	case []byte:
		source = v
	default:
		return errors.New("incompatible type for PriceRange")
	}

	return json.Unmarshal(source, pr)
}
