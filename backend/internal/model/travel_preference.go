package model

import (
	"database/sql/driver"
	"encoding/json"
	"fmt"
	"time"
)

type Budget struct {
	Type        string  `json:"type"`
	ExactBudget float64 `json:"exact_budget"`
}

func (b Budget) Value() (driver.Value, error) {
	return json.Marshal(b)
}

func (b *Budget) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return fmt.Errorf("failed to unmarshal Budget value: %v", value)
	}
	return json.Unmarshal(bytes, b)
}

type People struct {
	Adults   int `json:"adults"`
	Children int `json:"children"`
	Infants  int `json:"infants"`
	Pets     int `json:"pets"`
}

func (p People) Value() (driver.Value, error) {
	return json.Marshal(p)
}

func (p *People) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return fmt.Errorf("failed to unmarshal People: %v", value)
	}
	return json.Unmarshal(bytes, p)
}

type TravelTime struct {
	Type      string    `json:"type"`
	StartDate time.Time `json:"start_date"`
	EndDate   time.Time `json:"end_date"`
}

func (t TravelTime) Value() (driver.Value, error) {
	return json.Marshal(t)
}

func (t *TravelTime) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return fmt.Errorf("failed to unmarshal TravelTime: %v", value)
	}
	return json.Unmarshal(bytes, t)
}

type PersonalOption struct {
	Type        string `json:"type"` // "places", "activities", "accommodation"
	Name        string `json:"name"`
	Description string `json:"description"`
}

func (po PersonalOption) Value() (driver.Value, error) {
	return json.Marshal(po)
}

func (po *PersonalOption) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return fmt.Errorf("failed to unmarshal PersonalOption: %v", value)
	}
	return json.Unmarshal(bytes, po)
}

type ListPersonalOption []PersonalOption

func (l ListPersonalOption) Value() (driver.Value, error) {
	return json.Marshal(l)
}

func (l *ListPersonalOption) Scan(value interface{}) error {
	bytes, ok := value.([]byte)
	if !ok {
		return fmt.Errorf("failed to unmarshal ListPersonalOption: %v", value)
	}
	return json.Unmarshal(bytes, l)
}

type TravelPreference struct {
	TravelPreferenceID string           `gorm:"type:char(36);primaryKey" json:"travel_preference_id"`
	TripID             string           `gorm:"type:char(36);not null" json:"trip_id"`
	DestinationID      string           `gorm:"size:255" json:"destination_id"`
	Budget             Budget           `gorm:"type:json" json:"budget"`
	People             People           `gorm:"type:json" json:"people"`
	TravelTime         TravelTime       `gorm:"type:json" json:"travel_time"`
	PersonalOptions    []PersonalOption `gorm:"type:json" json:"personal_options"`

	Trip        *Trip        `json:"trip,omitempty"`
	Destination *Destination `json:"destination,omitempty"`
}
