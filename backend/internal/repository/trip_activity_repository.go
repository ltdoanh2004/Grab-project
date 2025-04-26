package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// TripActivityRepository defines data access methods for the TripActivity entity.
type TripActivityRepository interface {
	GetByID(tripActivityID string) (model.TripActivity, error)
	Create(tripActivity *model.TripActivity) error
	Update(tripActivity *model.TripActivity) error
	Delete(tripActivityID string) error
	GetByTripID(tripID string) ([]model.TripActivity, error)
}

// GormTripActivityRepository implements TripActivityRepository using GORM.
type GormTripActivityRepository struct {
	DB *gorm.DB
}

// NewTripActivityRepository returns a new GORM-based TripActivity repository.
func NewTripActivityRepository(db *gorm.DB) TripActivityRepository {
	return &GormTripActivityRepository{DB: db}
}

// Create saves a new TripActivity record.
func (r *GormTripActivityRepository) Create(tripActivity *model.TripActivity) error {
	return r.DB.Create(tripActivity).Error
}

// GetByID retrieves a TripActivity by its ID.
func (r *GormTripActivityRepository) GetByID(tripActivityID string) (model.TripActivity, error) {
	var tripActivity model.TripActivity
	if err := r.DB.First(&tripActivity, "trip_activity_id = ?", tripActivityID).Error; err != nil {
		return model.TripActivity{}, err
	}
	return tripActivity, nil
}

// Update modifies an existing TripActivity record.
func (r *GormTripActivityRepository) Update(tripActivity *model.TripActivity) error {
	return r.DB.Save(tripActivity).Error
}

// Delete removes a TripActivity record by its ID.
func (r *GormTripActivityRepository) Delete(tripActivityID string) error {
	return r.DB.Delete(&model.TripActivity{}, tripActivityID).Error
}

// GetByTripID retrieves all TripActivity records associated with a specific TripID.
func (r *GormTripActivityRepository) GetByTripID(tripDestinationID string) ([]model.TripActivity, error) {
	var tripActivities []model.TripActivity
	if err := r.DB.Where("trip_destination_id = ?", tripDestinationID).Find(&tripActivities).Error; err != nil {
		return nil, err
	}
	return tripActivities, nil
}
