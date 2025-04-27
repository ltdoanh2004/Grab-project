package service

import (
	"encoding/json"
	"fmt"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"
	"skeleton-internship-backend/internal/util"
	"strconv"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

type InsertDataService interface {
	InsertHotelData(filePath string) error
}

type insertDataService struct {
	accommodationRepo repository.AccommodationRepository
	imageRepo         repository.ImageRepository
	roomTypeRepo      repository.RoomTypeRepository
	db                *gorm.DB
}

func NewInsertDataService(
	accommodationRepo repository.AccommodationRepository,
	imageRepo repository.ImageRepository,
	roomTypeRepo repository.RoomTypeRepository,
	db *gorm.DB,
) InsertDataService {
	return &insertDataService{
		accommodationRepo: accommodationRepo,
		imageRepo:         imageRepo,
		roomTypeRepo:      roomTypeRepo,
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

		// Insert images
		for _, img := range accommodation.Images {
			img.AccommodationID = accommodation.AccommodationID
			img.ImageID = uuid.New().String()
			if err := tx.Create(&img).Error; err != nil {
				tx.Rollback()
				return err
			}
		}

		// Insert room types
		for _, rt := range accommodation.RoomTypes {
			rt.AccommodationID = accommodation.AccommodationID
			rt.RoomTypeID = uuid.New().String()
			if err := tx.Create(&rt).Error; err != nil {
				tx.Rollback()
				return err
			}
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

	var images []dto.CreateImageDTO
	if err := json.Unmarshal([]byte(record["images"]), &images); err != nil {
		return nil, fmt.Errorf("failed to unmarshal images: %w", err)
	}

	var roomTypes []dto.CreateRoomTypeDTO
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
	}

	// Map images and room types to their respective model structs
	accommodation.Images = s.mapImages(images, accommodation.AccommodationID)
	accommodation.RoomTypes = s.mapRoomTypes(roomTypes, accommodation.AccommodationID)

	return accommodation, nil
}

func (s *insertDataService) mapImages(imageDTOs []dto.CreateImageDTO, accommodationID string) []model.Image {
	var images []model.Image
	for _, img := range imageDTOs {
		images = append(images, model.Image{
			AccommodationID: accommodationID,
			Url:             img.Url,
			Alt:             img.Alt,
		})
	}
	return images
}

func (s *insertDataService) mapRoomTypes(roomTypeDTOs []dto.CreateRoomTypeDTO, accommodationID string) []model.RoomType {
	var roomTypes []model.RoomType
	for _, rt := range roomTypeDTOs {
		roomTypes = append(roomTypes, model.RoomType{
			AccommodationID: accommodationID,
			Name:            rt.Name,
			BedType:         rt.BedType,
			Price:           rt.Price,
			TaxesAndFees:    rt.Taxes,
			Occupancy:       rt.Occupancy,
			Conditions:      rt.Conditions,
		})
	}
	return roomTypes
}
