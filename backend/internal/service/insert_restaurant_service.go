package service

import (
	"encoding/json"
	"fmt"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/util"
	"strconv"
)

func (s *insertDataService) InsertRestaurantData(filePath string) error {
	records, err := util.ReadCSV(filePath)
	if err != nil {
		return err
	}

	tx := s.db.Begin()
	for _, record := range records {
		restaurant, err := s.mapRecordToRestaurant(record)
		if err != nil {
			tx.Rollback()
			return err
		}

		if err := tx.Create(restaurant).Error; err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit().Error
}

func (s *insertDataService) mapRecordToRestaurant(record map[string]string) (*model.Restaurant, error) {
	rating, err := strconv.ParseFloat(record["rating"], 64)
	if err != nil {
		return nil, err
	}

	numReviews, err := strconv.Atoi(record["num_reviews"])
	if err != nil {
		return nil, err
	}

	isDelivery, err := strconv.ParseBool(record["is_delivery"])
	if err != nil {
		return nil, err
	}

	isBooking, err := strconv.ParseBool(record["is_booking"])
	if err != nil {
		return nil, err
	}

	isOpening, err := strconv.ParseBool(record["is_opening"])
	if err != nil {
		return nil, err
	}

	var location model.Location
	if err := json.Unmarshal([]byte(record["location"]), &location); err != nil {
		return nil, fmt.Errorf("failed to unmarshal location: %w", err)
	}

	var reviews model.StringArray
	if err := json.Unmarshal([]byte(record["reviews"]), &reviews); err != nil {
		return nil, fmt.Errorf("failed to unmarshal reviews: %w", err)
	}

	var services model.StringArray
	if err := json.Unmarshal([]byte(record["services"]), &services); err != nil {
		return nil, fmt.Errorf("failed to unmarshal services: %w", err)
	}

	restaurant := &model.Restaurant{
		RestaurantID:   record["id"],
		DestinationID:  record["destination_id"],
		Name:           record["name"],
		Address:        record["address"],
		Rating:         rating,
		Phone:          record["phone"],
		PhotoURL:       record["photo_url"],
		URL:            record["url"],
		Location:       location,
		Reviews:        reviews,
		Services:       services,
		IsDelivery:     isDelivery,
		IsBooking:      isBooking,
		IsOpening:      isOpening,
		PriceRange:     record["price_range"],
		Description:    record["description"],
		Cuisines:       record["cuisines"],
		NumReviews:     numReviews,
		ExampleReviews: record["example_reviews"],
		MediaURLs:      record["media_urls"],
		MainImage:      record["main_image"],
		OpeningHours:   record["opening_hours"],
		ReviewSummary:  record["review_summary"],
	}

	return restaurant, nil
}
