package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// TripDestinationRepository defines data access methods for the TripDestination entity.
type TripDestinationRepository interface {
	GetByID(tripDestinationID uint) (model.TripDestination, error)
	Create(tripDestination *model.TripDestination) error
	Update(tripDestination *model.TripDestination) error
	Delete(tripDestinationID uint) error
	GetByTripID(tripID uint) ([]model.TripDestination, error)
}

// GormTripDestinationRepository implements TripDestinationRepository using GORM.
type GormTripDestinationRepository struct {
	DB *gorm.DB
}

// NewTripDestinationRepository returns a new GORM-based TripDestination repository.
func NewTripDestinationRepository(db *gorm.DB) TripDestinationRepository {
	return &GormTripDestinationRepository{DB: db}
}

// Create saves a new TripDestination record.
func (r *GormTripDestinationRepository) Create(tripDestination *model.TripDestination) error {
	return r.DB.Create(tripDestination).Error
}

// GetByID retrieves a TripDestination by its ID.
func (r *GormTripDestinationRepository) GetByID(tripDestinationID uint) (model.TripDestination, error) {
	var tripDestination model.TripDestination
	if err := r.DB.First(&tripDestination, tripDestinationID).Error; err != nil {
		return tripDestination, err
	}
	return tripDestination, nil
}

// Update modifies an existing TripDestination record.
func (r *GormTripDestinationRepository) Update(tripDestination *model.TripDestination) error {
	return r.DB.Save(tripDestination).Error
}

// Delete removes a TripDestination record by its ID.
func (r *GormTripDestinationRepository) Delete(tripDestinationID uint) error {
	return r.DB.Delete(&model.TripDestination{}, tripDestinationID).Error
}

// GetByTripID retrieves all TripDestination records associated with a specific TripID.
func (r *GormTripDestinationRepository) GetByTripID(tripID uint) ([]model.TripDestination, error) {
	var tripDestinations []model.TripDestination
	if err := r.DB.Where("trip_id = ?", tripID).Find(&tripDestinations).Error; err != nil {
		return nil, err
	}
	return tripDestinations, nil
}
