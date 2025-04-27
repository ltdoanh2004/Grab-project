package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

type ImageRepository interface {
	Create(image *model.Image) error
	GetByID(imageID string) (model.Image, error)
	Update(image *model.Image) error
	Delete(imageID string) error
	GetByAccommodationID(accommodationID string) ([]model.Image, error)
	GetAll() ([]model.Image, error)
}

type GormImageRepository struct {
	DB *gorm.DB
}

func NewImageRepository(db *gorm.DB) ImageRepository {
	return &GormImageRepository{DB: db}
}

func (r *GormImageRepository) Create(image *model.Image) error {
	return r.DB.Create(image).Error
}

func (r *GormImageRepository) GetByID(imageID string) (model.Image, error) {
	var image model.Image
	if err := r.DB.First(&image, "image_id = ?", imageID).Error; err != nil {
		return model.Image{}, err
	}
	return image, nil
}

func (r *GormImageRepository) Update(image *model.Image) error {
	return r.DB.Save(image).Error
}

func (r *GormImageRepository) Delete(imageID string) error {
	return r.DB.Delete(&model.Image{}, "image_id = ?", imageID).Error
}

func (r *GormImageRepository) GetByAccommodationID(accommodationID string) ([]model.Image, error) {
	var images []model.Image
	if err := r.DB.Where("accommodation_id = ?", accommodationID).Find(&images).Error; err != nil {
		return nil, err
	}
	return images, nil
}

func (r *GormImageRepository) GetAll() ([]model.Image, error) {
	var images []model.Image
	if err := r.DB.Find(&images).Error; err != nil {
		return nil, err
	}
	return images, nil
}
