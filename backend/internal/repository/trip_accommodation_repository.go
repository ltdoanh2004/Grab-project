package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// TripAccommodationRepository defines data access methods for the TripAccommodation entity.
type TripAccommodationRepository interface {
	GetByID(tripAccommodationID string) (model.TripAccommodation, error)
	Create(tripAccommodation *model.TripAccommodation) error
	Update(tripAccommodation *model.TripAccommodation) error
	Delete(tripAccommodationID string) error
	GetByTripID(tripID string) ([]model.TripAccommodation, error)
	GetByAccommodationID(accommodationID string) ([]model.TripAccommodation, error)
	GetAll() ([]model.TripAccommodation, error)
}

// GormTripAccommodationRepository implements TripAccommodationRepository using GORM.
type GormTripAccommodationRepository struct {
	DB *gorm.DB
}

// NewTripAccommodationRepository returns a new GORM-based TripAccommodation repository.
func NewTripAccommodationRepository(db *gorm.DB) TripAccommodationRepository {
	return &GormTripAccommodationRepository{DB: db}
}

// Create saves a new TripAccommodation record.
func (r *GormTripAccommodationRepository) Create(tripAccommodation *model.TripAccommodation) error {
	return r.DB.Create(tripAccommodation).Error
}

// GetByID retrieves a TripAccommodation by its ID.
func (r *GormTripAccommodationRepository) GetByID(tripAccommodationID string) (model.TripAccommodation, error) {
	var tripAccommodation model.TripAccommodation
	if err := r.DB.First(&tripAccommodation, "trip_accommodation_id = ?", tripAccommodationID).Error; err != nil {
		return model.TripAccommodation{}, err
	}
	return tripAccommodation, nil
}

// Update modifies an existing TripAccommodation record.
func (r *GormTripAccommodationRepository) Update(tripAccommodation *model.TripAccommodation) error {
	return r.DB.Save(tripAccommodation).Error
}

// Delete removes a TripAccommodation record by its ID.
func (r *GormTripAccommodationRepository) Delete(tripAccommodationID string) error {
	return r.DB.Delete(&model.TripAccommodation{}, tripAccommodationID).Error
}

// GetByTripID retrieves all TripAccommodation records associated with a specific TripID.
func (r *GormTripAccommodationRepository) GetByTripID(tripDestinationID string) ([]model.TripAccommodation, error) {
	var tripAccommodations []model.TripAccommodation
	if err := r.DB.Where("trip_destination_id = ?", tripDestinationID).Find(&tripAccommodations).Error; err != nil {
		return nil, err
	}
	return tripAccommodations, nil
}

// GetByAccommodationID retrieves all TripAccommodation records associated with a specific AccommodationID.
func (r *GormTripAccommodationRepository) GetByAccommodationID(accommodationID string) ([]model.TripAccommodation, error) {
	var tripAccommodations []model.TripAccommodation
	if err := r.DB.Where("accommodation_id = ?", accommodationID).Find(&tripAccommodations).Error; err != nil {
		return nil, err
	}
	return tripAccommodations, nil
}

// GetAll retrieves all TripAccommodation records.
func (r *GormTripAccommodationRepository) GetAll() ([]model.TripAccommodation, error) {
	var tripAccommodations []model.TripAccommodation
	if err := r.DB.Find(&tripAccommodations).Error; err != nil {
		return nil, err
	}
	return tripAccommodations, nil
}
