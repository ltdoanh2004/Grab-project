package service

import (
	"encoding/csv"
	"encoding/json"
	"os"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"
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
	records, err := s.readCSV(filePath)
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

		if err := tx.Create(accommodation).Error; err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit().Error
}

func (s *insertDataService) readCSV(filePath string) ([]map[string]string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	reader := csv.NewReader(f)
	header, err := reader.Read()
	if err != nil {
		return nil, err
	}

	var records []map[string]string
	for {
		record, err := reader.Read()
		if err != nil {
			break
		}
		recordMap := make(map[string]string)
		for i, value := range record {
			recordMap[header[i]] = value
		}
		records = append(records, recordMap)
	}

	return records, nil
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
		return nil, err
	}

	var roomTypes []dto.CreateRoomTypeDTO
	if err := json.Unmarshal([]byte(record["room_types"]), &roomTypes); err != nil {
		return nil, err
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
