package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// RestaurantRepository defines data access methods for the Restaurant entity.
type RestaurantRepository interface {
	GetByID(restaurantID uint) (model.Restaurant, error)
	Create(restaurant *model.Restaurant) error
	Update(restaurant *model.Restaurant) error
	Delete(restaurantID uint) error
	GetByDestinationID(destinationID uint) ([]model.Restaurant, error)
	GetAll() ([]model.Restaurant, error)
	GetWithFoods(restaurantID uint) (model.Restaurant, error)
	GetAllWithFoods() ([]model.Restaurant, error)
}

// GormRestaurantRepository implements RestaurantRepository using GORM.
type GormRestaurantRepository struct {
	DB *gorm.DB
}

// NewRestaurantRepository returns a new GORM-based Restaurant repository.
func NewRestaurantRepository(db *gorm.DB) RestaurantRepository {
	return &GormRestaurantRepository{DB: db}
}

// Create saves a new Restaurant record.
func (r *GormRestaurantRepository) Create(restaurant *model.Restaurant) error {
	return r.DB.Create(restaurant).Error
}

// GetByID retrieves a Restaurant by its ID.
func (r *GormRestaurantRepository) GetByID(restaurantID uint) (model.Restaurant, error) {
	var restaurant model.Restaurant
	if err := r.DB.First(&restaurant, restaurantID).Error; err != nil {
		return restaurant, err
	}
	return restaurant, nil
}

// Update modifies an existing Restaurant record.
func (r *GormRestaurantRepository) Update(restaurant *model.Restaurant) error {
	return r.DB.Save(restaurant).Error
}

// Delete removes a Restaurant record by its ID.
func (r *GormRestaurantRepository) Delete(restaurantID uint) error {
	return r.DB.Delete(&model.Restaurant{}, restaurantID).Error
}

// GetByDestinationID retrieves all Restaurant records associated with a specific DestinationID.
func (r *GormRestaurantRepository) GetByDestinationID(destinationID uint) ([]model.Restaurant, error) {
	var restaurants []model.Restaurant
	if err := r.DB.Where("destination_id = ?", destinationID).Find(&restaurants).Error; err != nil {
		return nil, err
	}
	return restaurants, nil
}

// GetAll retrieves all Restaurant records.
func (r *GormRestaurantRepository) GetAll() ([]model.Restaurant, error) {
	var restaurants []model.Restaurant
	if err := r.DB.Find(&restaurants).Error; err != nil {
		return nil, err
	}
	return restaurants, nil
}

// GetWithFoods retrieves a Restaurant by its ID with associated foods.
func (r *GormRestaurantRepository) GetWithFoods(restaurantID uint) (model.Restaurant, error) {
	var restaurant model.Restaurant
	if err := r.DB.Preload("Foods").First(&restaurant, restaurantID).Error; err != nil {
		return restaurant, err
	}
	return restaurant, nil
}

// GetAllWithFoods retrieves all Restaurant records with associated foods.
func (r *GormRestaurantRepository) GetAllWithFoods() ([]model.Restaurant, error) {
	var restaurants []model.Restaurant
	if err := r.DB.Preload("Foods").Find(&restaurants).Error; err != nil {
		return nil, err
	}
	return restaurants, nil
}
