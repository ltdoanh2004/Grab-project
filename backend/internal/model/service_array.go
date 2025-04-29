package model

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
)

type Service struct {
	Name string `json:"name"`
	URL  string `json:"url"`
	Type int    `json:"type"`
}

type ServiceArray []Service

func (sa ServiceArray) Value() (driver.Value, error) {
	if len(sa) == 0 {
		return "[]", nil
	}
	bytes, err := json.Marshal(sa)
	if err != nil {
		return nil, err
	}
	return string(bytes), nil
}

func (sa *ServiceArray) Scan(value interface{}) error {
	if value == nil {
		*sa = ServiceArray{}
		return nil
	}

	switch v := value.(type) {
	case []byte:
		return json.Unmarshal(v, sa)
	case string:
		return json.Unmarshal([]byte(v), sa)
	default:
		return errors.New("invalid type for ImageArray")
	}
}
