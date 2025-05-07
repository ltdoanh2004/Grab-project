package service

import (
	"encoding/json"
	"fmt"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/util"
	"strconv"
	"strings"

	"gorm.io/gorm"
)

type InsertDataService interface {
	InsertDestinationData(filePath string) error
	InsertHotelData(filePath string) error
	InsertRestaurantData(filePath string) error
	InsertPlaceData(filePath string) error
}

type insertDataService struct {
	db *gorm.DB
}

func NewInsertDataService(
	db *gorm.DB,
) InsertDataService {
	return &insertDataService{
		db: db,
	}
}

func (s *insertDataService) InsertHotelData(filePath string) error {
	records, err := util.ReadCSV(filePath)
	if err != nil {
		return err
	}
	// Begin transaction
	tx := s.db.Begin()
	for _, record := range records {
		accommodation, err := s.mapRecordToAccommodation(record)
		if err != nil {
			fmt.Println(record["id"])
			tx.Rollback()
			return err
		}

		// Insert accommodation
		if err := tx.Create(accommodation).Error; err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit().Error
}

func (s *insertDataService) mapRecordToAccommodation(record map[string]string) (*model.Accommodation, error) {
	price, err := strconv.ParseFloat(record["price"], 64)
	if err != nil {
		return nil, err
	}

	rating, err := strconv.ParseFloat(record["rating"], 64)
	if err != nil {
		return nil, err
	}

	elderlyFriendly, err := strconv.ParseBool(record["elderly_friendly"])
	if err != nil {
		return nil, err
	}

	// Clean and validate JSON strings
	imagesStr := record["images"]
	if imagesStr == "nan" {
		imagesStr = "[]"
	}
	roomTypesStr := record["room_types"]
	if roomTypesStr == "nan" {
		roomTypesStr = "[]"
	}

	var images model.ImageArray
	if err := json.Unmarshal([]byte(imagesStr), &images); err != nil {
		// Try to fix common JSON formatting issues
		imagesStr = strings.ReplaceAll(imagesStr, "'", "\"")
		imagesStr = strings.ReplaceAll(imagesStr, "~", "'")
		if err := json.Unmarshal([]byte(imagesStr), &images); err != nil {
			return nil, fmt.Errorf("failed to unmarshal images: %w", err)
		}
	}

	var roomTypes model.RoomTypeArray
	if len(strings.TrimSpace(roomTypesStr)) != 0 {
		if err := json.Unmarshal([]byte(roomTypesStr), &roomTypes); err != nil {
			// Try to fix common JSON formatting issues
			roomTypesStr = strings.ReplaceAll(roomTypesStr, "'", "\"")
			roomTypesStr = strings.ReplaceAll(roomTypesStr, "~", "'")

			if err := json.Unmarshal([]byte(roomTypesStr), &roomTypes); err != nil {
				return nil, fmt.Errorf("failed to unmarshal room types: %w", err)
			}
		}
	}

	accommodation := &model.Accommodation{
		AccommodationID: record["id"],
		DestinationID:   record["city"],
		Name:            record["name"],
		Link:            record["link"],
		Price:           price,
		TaxInfo:         record["tax_info"],
		Rating:          rating,
		Location:        record["location"],
		Description:     record["description"],
		City:            record["city"],
		ElderlyFriendly: elderlyFriendly,
		RoomInfo:        record["room_info"],
		Unit:            record["unit"],
		Images:          images,
		RoomTypes:       roomTypes,
	}

	return accommodation, nil
}
