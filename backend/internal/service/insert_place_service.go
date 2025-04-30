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
			fmt.Println(record["id"])
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
	price, err := strconv.ParseFloat(record["price"], 64)
	if err != nil {
		return nil, err
	}

	rating, err := strconv.ParseFloat(record["rating"], 64)
	if err != nil {
		return nil, err
	}

	var imageUrls model.StringArray
	var images model.ImageArray
	if len(record["image_urls"]) != 0 {
		if err := json.Unmarshal([]byte(record["image_urls"]), &imageUrls); err != nil {
			fmt.Println(record["image_urls"])
			return nil, fmt.Errorf("failed to unmarshal images: %w", err)
		}
	}
	for _, url := range imageUrls {
		images = append(images, model.Image{URL: url})
	}

	var reviews model.StringArray
	if len(record["reviews"]) != 0 {
		if err := json.Unmarshal([]byte(record["reviews"]), &reviews); err != nil {
			fmt.Println(record["reviews"])
			return nil, fmt.Errorf("failed to unmarshal reviews: %w", err)
		}
	}

	place := &model.Place{
		PlaceID:       record["id"],
		DestinationID: record["city"],
		Name:          record["name"],
		URL:           record["url"],
		Address:       record["address"],
		Duration:      record["duration"],
		Type:          record["type"],
		Categories:    record["categories"],
		Images:        images,
		MainImage:     record["main_image"],
		Price:         price,
		Rating:        rating,
		Description:   record["description"],
		OpeningHours:  record["opening_hours"],
		Reviews:       reviews,
	}

	return place, nil
}
