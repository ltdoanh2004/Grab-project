package service

import (
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"

	"github.com/google/uuid"
)

type AccommodationService interface {
	CreateAccommodation(accommodation *model.Accommodation) (string, error)
	GetByID(id string) (model.Accommodation, error)
	GetByIDWithAssociations(id string) (model.Accommodation, error)
}

type accommodationService struct {
	accommodationRepo repository.AccommodationRepository
	imageRepo         repository.ImageRepository
	roomTypeRepo      repository.RoomTypeRepository
}

func NewAccommodationService(
	accommodationRepo repository.AccommodationRepository,
	imageRepo repository.ImageRepository,
	roomTypeRepo repository.RoomTypeRepository,
) AccommodationService {
	return &accommodationService{
		accommodationRepo: accommodationRepo,
		imageRepo:         imageRepo,
		roomTypeRepo:      roomTypeRepo,
	}
}

func (s *accommodationService) CreateAccommodation(accommodation *model.Accommodation) (string, error) {
	// Generate UUID for accommodation
	accommodation.AccommodationID = uuid.New().String()

	// Begin transaction
	tx := s.accommodationRepo.(*repository.GormAccommodationRepository).DB.Begin()

	// Create accommodation
	if err := tx.Create(accommodation).Error; err != nil {
		tx.Rollback()
		return "", err
	}

	// Process images
	for i := range accommodation.Images {
		accommodation.Images[i].ImageID = uuid.New().String()
		accommodation.Images[i].AccommodationID = accommodation.AccommodationID
		if err := tx.Create(&accommodation.Images[i]).Error; err != nil {
			tx.Rollback()
			return "", err
		}
	}

	// Process room types
	for i := range accommodation.RoomTypes {
		accommodation.RoomTypes[i].RoomTypeID = uuid.New().String()
		accommodation.RoomTypes[i].AccommodationID = accommodation.AccommodationID
		if err := tx.Create(&accommodation.RoomTypes[i]).Error; err != nil {
			tx.Rollback()
			return "", err
		}
	}

	// Commit transaction
	err := tx.Commit().Error
	if err != nil {
		return "", err
	}
	return accommodation.AccommodationID, nil
}

func (s *accommodationService) GetByID(id string) (model.Accommodation, error) {
	return s.accommodationRepo.GetByID(id)
}

func (s *accommodationService) GetByIDWithAssociations(id string) (model.Accommodation, error) {
	return s.accommodationRepo.GetByIDWithAssociations(id)
}
