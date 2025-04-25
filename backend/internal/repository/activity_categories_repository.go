package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// ActivityCategoryRepository defines data access methods for the ActivityCategory entity.
type ActivityCategoryRepository interface {
	GetByID(categoryID string) (model.ActivityCategory, error)
	Create(category *model.ActivityCategory) error
	Update(category *model.ActivityCategory) error
	Delete(categoryID string) error
	GetAll() ([]model.ActivityCategory, error)
}

// GormActivityCategoryRepository implements ActivityCategoryRepository using GORM.
type GormActivityCategoryRepository struct {
	DB *gorm.DB
}

// NewActivityCategoryRepository returns a new GORM-based ActivityCategory repository.
func NewActivityCategoryRepository(db *gorm.DB) ActivityCategoryRepository {
	return &GormActivityCategoryRepository{DB: db}
}

// Create saves a new ActivityCategory record.
func (r *GormActivityCategoryRepository) Create(category *model.ActivityCategory) error {
	return r.DB.Create(category).Error
}

// GetByID retrieves an ActivityCategory by its ID.
func (r *GormActivityCategoryRepository) GetByID(categoryID string) (model.ActivityCategory, error) {
	var category model.ActivityCategory
	if err := r.DB.First(&category, "category_id = ?", categoryID).Error; err != nil {
		return model.ActivityCategory{}, err
	}
	return category, nil
}

// Update modifies an existing ActivityCategory record.
func (r *GormActivityCategoryRepository) Update(category *model.ActivityCategory) error {
	return r.DB.Save(category).Error
}

// Delete removes an ActivityCategory record by its ID.
func (r *GormActivityCategoryRepository) Delete(categoryID string) error {
	return r.DB.Delete(&model.ActivityCategory{}, categoryID).Error
}

// GetAll retrieves all ActivityCategory records.
func (r *GormActivityCategoryRepository) GetAll() ([]model.ActivityCategory, error) {
	var categories []model.ActivityCategory
	if err := r.DB.Find(&categories).Error; err != nil {
		return nil, err
	}
	return categories, nil
}
