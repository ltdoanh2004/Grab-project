package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// AccommodationRepository defines data access methods for the Accommodation entity.
type AccommodationRepository interface {
	GetByID(accommodationID uint) (model.Accommodation, error)
	Create(accommodation *model.Accommodation) error
	Update(accommodation *model.Accommodation) error
	Delete(accommodationID uint) error
	GetByDestinationID(destinationID uint) ([]model.Accommodation, error)
	GetAll() ([]model.Accommodation, error)
}

// GormAccommodationRepository implements AccommodationRepository using GORM.
type GormAccommodationRepository struct {
	DB *gorm.DB
}

// NewAccommodationRepository returns a new GORM-based Accommodation repository.
func NewAccommodationRepository(db *gorm.DB) AccommodationRepository {
	return &GormAccommodationRepository{DB: db}
}

// Create saves a new Accommodation record.
func (r *GormAccommodationRepository) Create(accommodation *model.Accommodation) error {
	return r.DB.Create(accommodation).Error
}

// GetByID retrieves an Accommodation by its ID.
func (r *GormAccommodationRepository) GetByID(accommodationID uint) (model.Accommodation, error) {
	var accommodation model.Accommodation
	if err := r.DB.First(&accommodation, accommodationID).Error; err != nil {
		return accommodation, err
	}
	return accommodation, nil
}

// Update modifies an existing Accommodation record.
func (r *GormAccommodationRepository) Update(accommodation *model.Accommodation) error {
	return r.DB.Save(accommodation).Error
}

// Delete removes an Accommodation record by its ID.
func (r *GormAccommodationRepository) Delete(accommodationID uint) error {
	return r.DB.Delete(&model.Accommodation{}, accommodationID).Error
}

// GetByDestinationID retrieves all Accommodation records associated with a specific DestinationID.
func (r *GormAccommodationRepository) GetByDestinationID(destinationID uint) ([]model.Accommodation, error) {
	var accommodations []model.Accommodation
	if err := r.DB.Where("destination_id = ?", destinationID).Find(&accommodations).Error; err != nil {
		return nil, err
	}
	return accommodations, nil
}

// GetAll retrieves all Accommodation records.
func (r *GormAccommodationRepository) GetAll() ([]model.Accommodation, error) {
	var accommodations []model.Accommodation
	if err := r.DB.Find(&accommodations).Error; err != nil {
		return nil, err
	}
	return accommodations, nil
}
