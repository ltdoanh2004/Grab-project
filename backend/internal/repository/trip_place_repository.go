package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// TripPlaceRepository defines data access methods for the TripPlace entity.
type TripPlaceRepository interface {
	GetByID(tripPlaceID string) (model.TripPlace, error)
	Create(tripPlace *model.TripPlace) error
	Update(tripPlace *model.TripPlace) error
	Delete(tripPlaceID string) error
	GetByTripID(tripID string) ([]model.TripPlace, error)
	UpdateByID(placeID string, updatedData map[string]interface{}) error
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
func (r *GormTripPlaceRepository) GetByID(tripPlaceID string) (model.TripPlace, error) {
	var tripPlace model.TripPlace
	if err := r.DB.First(&tripPlace, "trip_place_id = ?", tripPlaceID).Error; err != nil {
		return model.TripPlace{}, err
	}
	return tripPlace, nil
}

// Update modifies an existing TripPlace record.
func (r *GormTripPlaceRepository) Update(tripPlace *model.TripPlace) error {
	return r.DB.Save(tripPlace).Error
}

// Delete removes a TripPlace record by its ID.
func (r *GormTripPlaceRepository) Delete(tripPlaceID string) error {
	return r.DB.Delete(&model.TripPlace{}, tripPlaceID).Error
}

// GetByTripID retrieves all TripPlace records associated with a specific TripID.
func (r *GormTripPlaceRepository) GetByTripID(tripDestinationID string) ([]model.TripPlace, error) {
	var tripActivities []model.TripPlace
	if err := r.DB.Where("trip_destination_id = ?", tripDestinationID).Find(&tripActivities).Error; err != nil {
		return nil, err
	}
	return tripActivities, nil
}

func (r *GormTripPlaceRepository) UpdateByID(placeID string, updatedData map[string]interface{}) error {
	return r.DB.Model(&model.TripPlace{}).
		Where("trip_place_id = ?", placeID).
		Updates(updatedData).Error
}
