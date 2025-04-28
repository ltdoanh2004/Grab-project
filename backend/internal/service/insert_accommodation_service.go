package service

import (
	"encoding/json"
	"fmt"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"
	"skeleton-internship-backend/internal/util"
	"strconv"

	"gorm.io/gorm"
)

type InsertDataService interface {
	InsertHotelData(filePath string) error
}

type insertDataService struct {
	accommodationRepo repository.AccommodationRepository
	db                *gorm.DB
}

func NewInsertDataService(
	accommodationRepo repository.AccommodationRepository,
	db *gorm.DB,
) InsertDataService {
	return &insertDataService{
		accommodationRepo: accommodationRepo,
		db:                db,
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

	var images util.ImageArray
	if err := json.Unmarshal([]byte(record["images"]), &images); err != nil {
		return nil, fmt.Errorf("failed to unmarshal images: %w", err)
	}

	var roomTypes util.RoomTypeArray
	if err := json.Unmarshal([]byte(record["room_types"]), &roomTypes); err != nil {
		return nil, fmt.Errorf("failed to unmarshal room types: %w", err)
	}

	accommodation := &model.Accommodation{
		AccommodationID: record["hotel_id"],
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
