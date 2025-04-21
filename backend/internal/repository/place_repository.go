package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// PlaceRepository defines data access methods for the Place entity.
type PlaceRepository interface {
	GetByID(placeID uint) (model.Place, error)
	Create(place *model.Place) error
	Update(place *model.Place) error
	Delete(placeID uint) error
	GetByDestinationID(destinationID uint) ([]model.Place, error)
	GetAll() ([]model.Place, error)
	GetPopularPlaces(destinationID uint) ([]model.Place, error)
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

// GetByID retrieves a Place by its ID.
func (r *GormPlaceRepository) GetByID(placeID uint) (model.Place, error) {
	var place model.Place
	if err := r.DB.First(&place, placeID).Error; err != nil {
		return place, err
	}
	return place, nil
}

// Update modifies an existing Place record.
func (r *GormPlaceRepository) Update(place *model.Place) error {
	return r.DB.Save(place).Error
}

// Delete removes a Place record by its ID.
func (r *GormPlaceRepository) Delete(placeID uint) error {
	return r.DB.Delete(&model.Place{}, placeID).Error
}

// GetByDestinationID retrieves all Place records associated with a specific DestinationID.
func (r *GormPlaceRepository) GetByDestinationID(destinationID uint) ([]model.Place, error) {
	var places []model.Place
	if err := r.DB.Where("destination_id = ?", destinationID).Find(&places).Error; err != nil {
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

// GetPopularPlaces retrieves popular Place records associated with a specific DestinationID.
func (r *GormPlaceRepository) GetPopularPlaces(destinationID uint) ([]model.Place, error) {
	var places []model.Place
	if err := r.DB.Where("destination_id = ?", destinationID).Order("popularity_score desc").Find(&places).Error; err != nil {
		return nil, err
	}
	return places, nil
}
