package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// PlaceCategoryRepository defines data access methods for the PlaceCategory entity.
type PlaceCategoryRepository interface {
	GetByID(categoryID string) (model.PlaceCategory, error)
	Create(category *model.PlaceCategory) error
	Update(category *model.PlaceCategory) error
	Delete(categoryID string) error
	GetAll() ([]model.PlaceCategory, error)
}

// GormPlaceCategoryRepository implements PlaceCategoryRepository using GORM.
type GormPlaceCategoryRepository struct {
	DB *gorm.DB
}

// NewPlaceCategoryRepository returns a new GORM-based PlaceCategory repository.
func NewPlaceCategoryRepository(db *gorm.DB) PlaceCategoryRepository {
	return &GormPlaceCategoryRepository{DB: db}
}

// Create saves a new PlaceCategory record.
func (r *GormPlaceCategoryRepository) Create(category *model.PlaceCategory) error {
	return r.DB.Create(category).Error
}

// GetByID retrieves an PlaceCategory by its ID.
func (r *GormPlaceCategoryRepository) GetByID(categoryID string) (model.PlaceCategory, error) {
	var category model.PlaceCategory
	if err := r.DB.First(&category, "category_id = ?", categoryID).Error; err != nil {
		return model.PlaceCategory{}, err
	}
	return category, nil
}

// Update modifies an existing PlaceCategory record.
func (r *GormPlaceCategoryRepository) Update(category *model.PlaceCategory) error {
	return r.DB.Save(category).Error
}

// Delete removes an PlaceCategory record by its ID.
func (r *GormPlaceCategoryRepository) Delete(categoryID string) error {
	return r.DB.Delete(&model.PlaceCategory{}, categoryID).Error
}

// GetAll retrieves all PlaceCategory records.
func (r *GormPlaceCategoryRepository) GetAll() ([]model.PlaceCategory, error) {
	var categories []model.PlaceCategory
	if err := r.DB.Find(&categories).Error; err != nil {
		return nil, err
	}
	return categories, nil
}
