package service

import (
	"encoding/json"
	"fmt"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/util"
	"strconv"
	"strings"
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
			fmt.Println(record["id"])
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
		fmt.Println("rating: ", record["rating"])
		return nil, err
	}
	var isDelivery bool
	if len(record["is_delivery"]) != 0 {
		isDelivery, err = strconv.ParseBool(record["is_delivery"])
		if err != nil {
			fmt.Println("Is delivery: ", record["is_delivery"])
			return nil, err
		}
	}

	var isBooking bool
	if len(record["is_booking"]) != 0 {
		isBooking, err = strconv.ParseBool(record["is_booking"])
		if err != nil {
			fmt.Println("Is booking: ", record["is_booking"])
			return nil, err
		}
	}

	var isOpening bool
	if len(record["is_opening"]) != 0 {
		isOpening, err = strconv.ParseBool(record["is_opening"])
		if err != nil {
			fmt.Println("Is opening: ", record["is_opening"])
			return nil, err
		}
	}

	var location model.Location
	if len(strings.TrimSpace(record["location"])) != 0 {
		if err := json.Unmarshal([]byte(record["location"]), &location); err != nil {
			fmt.Println(record["location"])
			return nil, fmt.Errorf("failed to unmarshal location: %w", err)
		}
	}

	var services model.ServiceArray
	if len(strings.TrimSpace(record["services"])) != 0 {
		if err := json.Unmarshal([]byte(record["services"]), &services); err != nil {
			fmt.Println(record)
			return nil, fmt.Errorf("failed to unmarshal services: %w", err)
		}
	}

	restaurant := &model.Restaurant{
		RestaurantID:  record["id"],
		DestinationID: record["city"],
		Name:          record["name"],
		Address:       record["address"],
		Rating:        rating,
		Phone:         record["phone"],
		PhotoURL:      record["photo_url"],
		URL:           record["url"],
		Location:      location,
		Reviews:       record["reviews"],
		Services:      services,
		IsDelivery:    isDelivery,
		IsBooking:     isBooking,
		IsOpening:     isOpening,
		PriceRange:    record["price_range"],
		Description:   record["description"],
		Cuisines:      record["cuisines"],
		OpeningHours:  record["opening_hours"],
	}

	return restaurant, nil
}
