package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

type Repository interface {
	Create(todo *model.Todo) error
	FindAll() ([]model.Todo, error)
	FindByID(id uint) (*model.Todo, error)
	Update(todo *model.Todo) error
	Delete(id uint) error
}

type repository struct {
	db *gorm.DB
}

func NewRepository(db *gorm.DB) Repository {
	return &repository{db: db}
}

func (r *repository) Create(todo *model.Todo) error {
	return r.db.Create(todo).Error
}

func (r *repository) FindAll() ([]model.Todo, error) {
	var todos []model.Todo
	err := r.db.Find(&todos).Error
	return todos, err
}

func (r *repository) FindByID(id uint) (*model.Todo, error) {
	var todo model.Todo
	err := r.db.First(&todo, id).Error
	if err != nil {
		return nil, err
	}
	return &todo, nil
}

func (r *repository) Update(todo *model.Todo) error {
	return r.db.Save(todo).Error
}

func (r *repository) Delete(id uint) error {
	return r.db.Delete(&model.Todo{}, id).Error
}
