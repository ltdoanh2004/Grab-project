package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// TravelPreferenceRepository defines data access methods for the TravelPreference entity.
type TravelPreferenceRepository interface {
	GetByID(id string) (model.TravelPreference, error)
	Create(tp *model.TravelPreference) error
	Update(tp *model.TravelPreference) error
	Delete(id string) error
	GetByTripID(id string) (model.TravelPreference, error)
	GetAll() ([]model.TravelPreference, error)
	GetWithAssociations(id string) (model.TravelPreference, error)
	GetAllWithAssociations() ([]model.TravelPreference, error)
}

// GormTravelPreferenceRepository implements TravelPreferenceRepository using GORM.
type GormTravelPreferenceRepository struct {
	DB *gorm.DB
}

// NewTravelPreferenceRepository returns a new GORM-based TravelPreference repository.
func NewTravelPreferenceRepository(db *gorm.DB) TravelPreferenceRepository {
	return &GormTravelPreferenceRepository{DB: db}
}

// Create saves a new TravelPreference record.
func (r *GormTravelPreferenceRepository) Create(tp *model.TravelPreference) error {
	return r.DB.Create(tp).Error
}

// GetByID retrieves a TravelPreference by its ID.
func (r *GormTravelPreferenceRepository) GetByID(id string) (model.TravelPreference, error) {
	var tp model.TravelPreference
	if err := r.DB.First(&tp, "travel_preference_id = ?", id).Error; err != nil {
		return model.TravelPreference{}, err
	}
	return tp, nil
}

// GetByID retrieves a TravelPreference by its ID.
func (r *GormTravelPreferenceRepository) GetByTripID(id string) (model.TravelPreference, error) {
	var tp model.TravelPreference
	if err := r.DB.First(&tp, "trip_id = ?", id).Error; err != nil {
		return model.TravelPreference{}, err
	}
	return tp, nil
}

// Update modifies an existing TravelPreference record.
func (r *GormTravelPreferenceRepository) Update(tp *model.TravelPreference) error {
	return r.DB.Model(&model.TravelPreference{}).
		Where("travel_preference_id = ?", tp.TravelPreferenceID).
		Updates(tp).Error
}

// Delete removes a TravelPreference record by its ID.
func (r *GormTravelPreferenceRepository) Delete(id string) error {
	return r.DB.Delete(&model.TravelPreference{}, "travel_preference_id = ?", id).Error
}

// GetAll retrieves all TravelPreference records.
func (r *GormTravelPreferenceRepository) GetAll() ([]model.TravelPreference, error) {
	var tps []model.TravelPreference
	if err := r.DB.Find(&tps).Error; err != nil {
		return nil, err
	}
	return tps, nil
}

// GetWithAssociations retrieves a TravelPreference by its ID with associated records.
func (r *GormTravelPreferenceRepository) GetWithAssociations(id string) (model.TravelPreference, error) {
	var tp model.TravelPreference
	if err := r.DB.
		Preload("Trip").
		Preload("Destination").
		First(&tp, "travel_preference_id = ?", id).Error; err != nil {
		return tp, err
	}
	return tp, nil
}

// GetAllWithAssociations retrieves all TravelPreference records with associated records.
func (r *GormTravelPreferenceRepository) GetAllWithAssociations() ([]model.TravelPreference, error) {
	var tps []model.TravelPreference
	if err := r.DB.
		Preload("Trip").
		Preload("Destination").
		Find(&tps).Error; err != nil {
		return nil, err
	}
	return tps, nil
}
