package service

import (
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"

	"github.com/google/uuid"
)

type RestaurantService interface {
	CreateRestaurant(restaurant *model.Restaurant) (string, error)
	GetByID(id string) (model.Restaurant, error)
	GetWithFoods(id string) (model.Restaurant, error)
	GetByDestinationID(destinationID string) ([]model.Restaurant, error)
}

type restaurantService struct {
	restaurantRepo repository.RestaurantRepository
}

func NewRestaurantService(
	restaurantRepo repository.RestaurantRepository,
) RestaurantService {
	return &restaurantService{
		restaurantRepo: restaurantRepo,
	}
}

func (s *restaurantService) CreateRestaurant(restaurant *model.Restaurant) (string, error) {
	// Generate UUID for restaurant
	restaurant.RestaurantID = uuid.New().String()

	// Begin transaction
	tx := s.restaurantRepo.(*repository.GormRestaurantRepository).DB.Begin()

	// Create restaurant
	if err := tx.Create(restaurant).Error; err != nil {
		tx.Rollback()
		return "", err
	}

	// Commit transaction
	if err := tx.Commit().Error; err != nil {
		return "", err
	}
	return restaurant.RestaurantID, nil
}

func (s *restaurantService) GetByID(id string) (model.Restaurant, error) {
	return s.restaurantRepo.GetByID(id)
}

func (s *restaurantService) GetWithFoods(id string) (model.Restaurant, error) {
	return s.restaurantRepo.GetWithFoods(id)
}

func (s *restaurantService) GetByDestinationID(destinationID string) ([]model.Restaurant, error) {
	return s.restaurantRepo.GetByDestinationID(destinationID)
}
