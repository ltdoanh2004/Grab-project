package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// TripRepository defines data access methods for the Trip entity.
type TripRepository interface {
	GetByID(tripID string) (model.Trip, error)
	Create(trip *model.Trip) error
	Update(trip *model.Trip) error
	Delete(tripID string) error
	GetByUserID(userID uint) ([]model.Trip, error)
	GetAll() ([]model.Trip, error)
	GetWithAssociations(tripID string) (model.Trip, error)
	GetAllWithAssociations() ([]model.Trip, error)
}

// GormTripRepository implements TripRepository using GORM.
type GormTripRepository struct {
	DB *gorm.DB
}

// NewTripRepository returns a new GORM-based Trip repository.
func NewTripRepository(db *gorm.DB) TripRepository {
	return &GormTripRepository{DB: db}
}

// Create saves a new Trip record.
func (r *GormTripRepository) Create(trip *model.Trip) error {
	return r.DB.Create(trip).Error
}

// GetByID retrieves a Trip by its ID.
func (r *GormTripRepository) GetByID(tripID string) (model.Trip, error) {
	var trip model.Trip
	if err := r.DB.First(&trip, tripID).Error; err != nil {
		return trip, err
	}
	return trip, nil
}

// Update modifies an existing Trip record.
func (r *GormTripRepository) Update(trip *model.Trip) error {
	return r.DB.Save(trip).Error
}

// Delete removes a Trip record by its ID.
func (r *GormTripRepository) Delete(tripID string) error {
	return r.DB.Delete(&model.Trip{}, tripID).Error
}

// GetByUserID retrieves all Trip records associated with a specific UserID.
func (r *GormTripRepository) GetByUserID(userID uint) ([]model.Trip, error) {
	var trips []model.Trip
	if err := r.DB.Where("user_id = ?", userID).Find(&trips).Error; err != nil {
		return nil, err
	}
	return trips, nil
}

// GetAll retrieves all Trip records.
func (r *GormTripRepository) GetAll() ([]model.Trip, error) {
	var trips []model.Trip
	if err := r.DB.Find(&trips).Error; err != nil {
		return nil, err
	}
	return trips, nil
}

// GetWithAssociations retrieves a Trip by its ID with associated records.
func (r *GormTripRepository) GetWithAssociations(tripID string) (model.Trip, error) {
	var trip model.Trip
	if err := r.DB.Preload("Destinations").First(&trip, tripID).Error; err != nil {
		return trip, err
	}
	return trip, nil
}

// GetAllWithAssociations retrieves all Trip records with associated records.
func (r *GormTripRepository) GetAllWithAssociations() ([]model.Trip, error) {
	var trips []model.Trip
	if err := r.DB.Preload("Destinations").Find(&trips).Error; err != nil {
		return nil, err
	}
	return trips, nil
}
