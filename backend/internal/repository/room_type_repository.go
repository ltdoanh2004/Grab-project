package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

type RoomTypeRepository interface {
	Create(roomType *model.RoomType) error
	GetByID(roomTypeID string) (model.RoomType, error)
	Update(roomType *model.RoomType) error
	Delete(roomTypeID string) error
	GetByAccommodationID(accommodationID string) ([]model.RoomType, error)
	GetAll() ([]model.RoomType, error)
}

type GormRoomTypeRepository struct {
	DB *gorm.DB
}

func NewRoomTypeRepository(db *gorm.DB) RoomTypeRepository {
	return &GormRoomTypeRepository{DB: db}
}

func (r *GormRoomTypeRepository) Create(roomType *model.RoomType) error {
	return r.DB.Create(roomType).Error
}

func (r *GormRoomTypeRepository) GetByID(roomTypeID string) (model.RoomType, error) {
	var roomType model.RoomType
	if err := r.DB.First(&roomType, "room_type_id = ?", roomTypeID).Error; err != nil {
		return model.RoomType{}, err
	}
	return roomType, nil
}

func (r *GormRoomTypeRepository) Update(roomType *model.RoomType) error {
	return r.DB.Save(roomType).Error
}

func (r *GormRoomTypeRepository) Delete(roomTypeID string) error {
	return r.DB.Delete(&model.RoomType{}, "room_type_id = ?", roomTypeID).Error
}

func (r *GormRoomTypeRepository) GetByAccommodationID(accommodationID string) ([]model.RoomType, error) {
	var roomTypes []model.RoomType
	if err := r.DB.Where("accommodation_id = ?", accommodationID).Find(&roomTypes).Error; err != nil {
		return nil, err
	}
	return roomTypes, nil
}

func (r *GormRoomTypeRepository) GetAll() ([]model.RoomType, error) {
	var roomTypes []model.RoomType
	if err := r.DB.Find(&roomTypes).Error; err != nil {
		return nil, err
	}
	return roomTypes, nil
}
