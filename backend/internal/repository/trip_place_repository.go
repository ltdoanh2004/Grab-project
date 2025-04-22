package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// TripPlaceRepository defines data access methods for the TripPlace entity.
type TripPlaceRepository interface {
	GetByID(tripPlaceID uint) (model.TripPlace, error)
	Create(tripPlace *model.TripPlace) error
	Update(tripPlace *model.TripPlace) error
	Delete(tripPlaceID uint) error
	GetByTripID(tripID uint) ([]model.TripPlace, error)
	GetAllWithAssociations() ([]model.TripPlace, error)
	GetWithAssociations(tripPlaceID uint) (model.TripPlace, error)
}

// GormTripPlaceRepository implements TripPlaceRepository using GORM.
type GormTripPlaceRepository struct {
	DB *gorm.DB
}

// NewTripPlaceRepository returns a new GORM-based TripPlace repository.
func NewTripPlaceRepository(db *gorm.DB) TripPlaceRepository {
	return &GormTripPlaceRepository{DB: db}
}

// Create saves a new TripPlace record.
func (r *GormTripPlaceRepository) Create(tripPlace *model.TripPlace) error {
	return r.DB.Create(tripPlace).Error
}

// GetByID retrieves a TripPlace by its ID.
func (r *GormTripPlaceRepository) GetByID(tripPlaceID uint) (model.TripPlace, error) {
	var tripPlace model.TripPlace
	if err := r.DB.First(&tripPlace, tripPlaceID).Error; err != nil {
		return tripPlace, err
	}
	return tripPlace, nil
}

// Update modifies an existing TripPlace record.
func (r *GormTripPlaceRepository) Update(tripPlace *model.TripPlace) error {
	return r.DB.Save(tripPlace).Error
}

// Delete removes a TripPlace record by its ID.
func (r *GormTripPlaceRepository) Delete(tripPlaceID uint) error {
	return r.DB.Delete(&model.TripPlace{}, tripPlaceID).Error
}

// GetByTripID retrieves all TripPlace records associated with a specific TripID.
func (r *GormTripPlaceRepository) GetByTripID(tripID uint) ([]model.TripPlace, error) {
	var tripPlaces []model.TripPlace
	if err := r.DB.Where("trip_id = ?", tripID).Find(&tripPlaces).Error; err != nil {
		return nil, err
	}
	return tripPlaces, nil
}

// GetAllWithAssociations retrieves all TripPlace records with associated records.
func (r *GormTripPlaceRepository) GetAllWithAssociations() ([]model.TripPlace, error) {
	var tripPlaces []model.TripPlace
	if err := r.DB.Preload("Trip").Preload("Place").Find(&tripPlaces).Error; err != nil {
		return nil, err
	}
	return tripPlaces, nil
}

// GetWithAssociations retrieves a TripPlace by its ID with associated records.
func (r *GormTripPlaceRepository) GetWithAssociations(tripPlaceID uint) (model.TripPlace, error) {
	var tripPlace model.TripPlace
	if err := r.DB.Preload("Trip").Preload("Place").First(&tripPlace, tripPlaceID).Error; err != nil {
		return tripPlace, err
	}
	return tripPlace, nil
}
