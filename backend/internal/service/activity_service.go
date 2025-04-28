package service

import (
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"

	"github.com/google/uuid"
)

type PlaceService interface {
	CreatePlace(place *model.Place) (string, error)
	GetByID(id string) (model.Place, error)
	GetWithCategory(id string) (model.Place, error)
	GetByDestinationID(destinationID string) ([]model.Place, error)
	GetByCategoryID(categoryID string) ([]model.Place, error)
}

type placeService struct {
	placeRepo repository.PlaceRepository
}

func NewPlaceService(
	placeRepo repository.PlaceRepository,
) PlaceService {
	return &placeService{
		placeRepo: placeRepo,
	}
}

func (s *placeService) CreatePlace(place *model.Place) (string, error) {
	// Generate UUID for place
	place.PlaceID = uuid.New().String()

	// Begin transaction
	tx := s.placeRepo.(*repository.GormPlaceRepository).DB.Begin()

	// Create place
	if err := tx.Create(place).Error; err != nil {
		tx.Rollback()
		return "", err
	}

	// Commit transaction
	if err := tx.Commit().Error; err != nil {
		return "", err
	}
	return place.PlaceID, nil
}

func (s *placeService) GetByID(id string) (model.Place, error) {
	return s.placeRepo.GetByID(id)
}

func (s *placeService) GetWithCategory(id string) (model.Place, error) {
	return s.placeRepo.GetWithCategory(id)
}

func (s *placeService) GetByDestinationID(destinationID string) ([]model.Place, error) {
	return s.placeRepo.GetByDestinationID(destinationID)
}

func (s *placeService) GetByCategoryID(categoryID string) ([]model.Place, error) {
	return s.placeRepo.GetByCategoryID(categoryID)
}
