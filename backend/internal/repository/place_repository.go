package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// PlaceRepository defines data access methods for the Place entity.
type PlaceRepository interface {
	GetByID(placeID string) (model.Place, error)
	Create(place *model.Place) error
	Update(place *model.Place) error
	Delete(placeID string) error
	GetByDestinationID(destinationID string) ([]model.Place, error)
	GetByCategoryID(categoryID string) ([]model.Place, error)
	GetAll() ([]model.Place, error)
	GetWithCategory(placeID string) (model.Place, error)
	GetAllWithCategory() ([]model.Place, error)
}

// GormPlaceRepository implements PlaceRepository using GORM.
type GormPlaceRepository struct {
	DB *gorm.DB
}

// NewPlaceRepository returns a new GORM-based Place repository.
func NewPlaceRepository(db *gorm.DB) PlaceRepository {
	return &GormPlaceRepository{DB: db}
}

// Create saves a new Place record.
func (r *GormPlaceRepository) Create(place *model.Place) error {
	return r.DB.Create(place).Error
}

// GetByID retrieves an Place by its ID.
func (r *GormPlaceRepository) GetByID(placeID string) (model.Place, error) {
	var place model.Place
	if err := r.DB.First(&place, "place_id = ?", placeID).Error; err != nil {
		return model.Place{}, err
	}
	return place, nil
}

// Update modifies an existing Place record.
func (r *GormPlaceRepository) Update(place *model.Place) error {
	return r.DB.Save(place).Error
}

// Delete removes an Place record by its ID.
func (r *GormPlaceRepository) Delete(placeID string) error {
	return r.DB.Delete(&model.Place{}, placeID).Error
}

// GetByDestinationID retrieves all Place records associated with a specific DestinationID.
func (r *GormPlaceRepository) GetByDestinationID(destinationID string) ([]model.Place, error) {
	var places []model.Place
	if err := r.DB.Where("destination_id = ?", destinationID).Find(&places).Error; err != nil {
		return nil, err
	}
	return places, nil
}

// GetByCategoryID retrieves all Place records associated with a specific CategoryID.
func (r *GormPlaceRepository) GetByCategoryID(categoryID string) ([]model.Place, error) {
	var places []model.Place
	if err := r.DB.Joins("JOIN place_category_places ON places.place_id = place_category_places.place_id").
		Where("place_category_places.category_id = ?", categoryID).
		Find(&places).Error; err != nil {
		return nil, err
	}
	return places, nil
}

// GetAll retrieves all Place records.
func (r *GormPlaceRepository) GetAll() ([]model.Place, error) {
	var places []model.Place
	if err := r.DB.Find(&places).Error; err != nil {
		return nil, err
	}
	return places, nil
}

// GetWithCategory retrieves a Place by its ID with associated categories.
func (r *GormPlaceRepository) GetWithCategory(placeID string) (model.Place, error) {
	var place model.Place
	if err := r.DB.Preload("Categories").First(&place, "place_id = ?", placeID).Error; err != nil {
		return place, err
	}
	return place, nil
}

// GetAllWithCategory retrieves all Place records with associated categories.
func (r *GormPlaceRepository) GetAllWithCategory() ([]model.Place, error) {
	var places []model.Place
	if err := r.DB.Preload("Categories").Find(&places).Error; err != nil {
		return nil, err
	}
	return places, nil
}
