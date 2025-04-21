package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// DestinationRepository defines data access methods for the Destination entity.
type DestinationRepository interface {
	GetByID(destinationID uint) (model.Destination, error)
	Create(destination *model.Destination) error
	Update(destination *model.Destination) error
	Delete(destinationID uint) error
	GetAll() ([]model.Destination, error)
}

// GormDestinationRepository implements DestinationRepository using GORM.
type GormDestinationRepository struct {
	DB *gorm.DB
}

// NewDestinationRepository returns a new GORM-based Destination repository.
func NewDestinationRepository(db *gorm.DB) DestinationRepository {
	return &GormDestinationRepository{DB: db}
}

// Create saves a new Destination record.
func (r *GormDestinationRepository) Create(destination *model.Destination) error {
	return r.DB.Create(destination).Error
}

// GetByID retrieves a Destination by its ID.
func (r *GormDestinationRepository) GetByID(destinationID uint) (model.Destination, error) {
	var destination model.Destination
	if err := r.DB.First(&destination, destinationID).Error; err != nil {
		return destination, err
	}
	return destination, nil
}

// Update modifies an existing Destination record.
func (r *GormDestinationRepository) Update(destination *model.Destination) error {
	return r.DB.Save(destination).Error
}

// Delete removes a Destination record by its ID.
func (r *GormDestinationRepository) Delete(destinationID uint) error {
	return r.DB.Delete(&model.Destination{}, destinationID).Error
}

// GetAll retrieves all Destination records.
func (r *GormDestinationRepository) GetAll() ([]model.Destination, error) {
	var destinations []model.Destination
	if err := r.DB.Find(&destinations).Error; err != nil {
		return nil, err
	}
	return destinations, nil
}
