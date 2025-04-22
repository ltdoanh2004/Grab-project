package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// ActivityRepository defines data access methods for the Activity entity.
type ActivityRepository interface {
	GetByID(activityID uint) (model.Activity, error)
	Create(activity *model.Activity) error
	Update(activity *model.Activity) error
	Delete(activityID uint) error
	GetByDestinationID(destinationID uint) ([]model.Activity, error)
	GetByCategoryID(categoryID uint) ([]model.Activity, error)
	GetAll() ([]model.Activity, error)
	GetWithCategory(activityID uint) (model.Activity, error)
	GetAllWithCategory() ([]model.Activity, error)
}

// GormActivityRepository implements ActivityRepository using GORM.
type GormActivityRepository struct {
	DB *gorm.DB
}

// NewActivityRepository returns a new GORM-based Activity repository.
func NewActivityRepository(db *gorm.DB) ActivityRepository {
	return &GormActivityRepository{DB: db}
}

// Create saves a new Activity record.
func (r *GormActivityRepository) Create(activity *model.Activity) error {
	return r.DB.Create(activity).Error
}

// GetByID retrieves an Activity by its ID.
func (r *GormActivityRepository) GetByID(activityID uint) (model.Activity, error) {
	var activity model.Activity
	if err := r.DB.First(&activity, activityID).Error; err != nil {
		return activity, err
	}
	return activity, nil
}

// Update modifies an existing Activity record.
func (r *GormActivityRepository) Update(activity *model.Activity) error {
	return r.DB.Save(activity).Error
}

// Delete removes an Activity record by its ID.
func (r *GormActivityRepository) Delete(activityID uint) error {
	return r.DB.Delete(&model.Activity{}, activityID).Error
}

// GetByDestinationID retrieves all Activity records associated with a specific DestinationID.
func (r *GormActivityRepository) GetByDestinationID(destinationID uint) ([]model.Activity, error) {
	var activities []model.Activity
	if err := r.DB.Where("destination_id = ?", destinationID).Find(&activities).Error; err != nil {
		return nil, err
	}
	return activities, nil
}

// GetByCategoryID retrieves all Activity records associated with a specific CategoryID.
func (r *GormActivityRepository) GetByCategoryID(categoryID uint) ([]model.Activity, error) {
	var activities []model.Activity
	if err := r.DB.Where("category_id = ?", categoryID).Find(&activities).Error; err != nil {
		return nil, err
	}
	return activities, nil
}

// GetAll retrieves all Activity records.
func (r *GormActivityRepository) GetAll() ([]model.Activity, error) {
	var activities []model.Activity
	if err := r.DB.Find(&activities).Error; err != nil {
		return nil, err
	}
	return activities, nil
}

// GetWithCategory retrieves an Activity by its ID with associated category.
func (r *GormActivityRepository) GetWithCategory(activityID uint) (model.Activity, error) {
	var activity model.Activity
	if err := r.DB.Preload("ActivityCategory").First(&activity, activityID).Error; err != nil {
		return activity, err
	}
	return activity, nil
}

// GetAllWithCategory retrieves all Activity records with associated categories.
func (r *GormActivityRepository) GetAllWithCategory() ([]model.Activity, error) {
	var activities []model.Activity
	if err := r.DB.Preload("ActivityCategory").Find(&activities).Error; err != nil {
		return nil, err
	}
	return activities, nil
}
