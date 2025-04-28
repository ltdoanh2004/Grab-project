package service

import (
	"encoding/json"
	"fmt"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/util"
	"strconv"
)

func (s *insertDataService) InsertPlaceData(filePath string) error {
	records, err := util.ReadCSV(filePath)
	if err != nil {
		return err
	}

	tx := s.db.Begin()
	for _, record := range records {
		place, err := s.mapRecordToPlace(record)
		if err != nil {
			tx.Rollback()
			return err
		}

		if err := tx.Create(place).Error; err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit().Error
}

func (s *insertDataService) mapRecordToPlace(record map[string]string) (*model.Place, error) {
	rating, err := strconv.ParseFloat(record["rating"], 64)
	if err != nil {
		return nil, err
	}

	var images model.ImageArray
	if err := json.Unmarshal([]byte(record["images"]), &images); err != nil {
		return nil, fmt.Errorf("failed to unmarshal images: %w", err)
	}

	var reviews model.StringArray
	if err := json.Unmarshal([]byte(record["reviews"]), &reviews); err != nil {
		return nil, fmt.Errorf("failed to unmarshal reviews: %w", err)
	}

	place := &model.Place{
		PlaceID:       record["place_id"],
		DestinationID: record["destination_id"],
		Name:          record["name"],
		URL:           record["url"],
		Address:       record["address"],
		Duration:      record["duration"],
		Type:          record["type"],
		Categories:    record["categories"],
		Images:        images,
		MainImage:     record["main_image"],
		Price:         record["price"],
		Rating:        rating,
		Description:   record["description"],
		OpeningHours:  record["opening_hours"],
		Reviews:       reviews,
	}

	return place, nil
}
