package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// UserRepository defines data access methods for the User entity.
type UserRepository interface {
	GetByID(userID string) (model.User, error)
	GetByUsername(username string) (model.User, error)
	Update(user *model.User) error
	Create(user *model.User) error
}

// GormUserRepository implements UserRepository using GORM.
type GormUserRepository struct {
	DB *gorm.DB
}

// NewUserRepository returns a new GORM-based user repository.
func NewUserRepository(db *gorm.DB) UserRepository {
	return &GormUserRepository{DB: db}
}

// Create saves a new user record.
func (r *GormUserRepository) Create(user *model.User) error {
	return r.DB.Create(user).Error
}

// Create saves a new user record.
func (r *GormUserRepository) Update(user *model.User) error {
	return r.DB.Save(user).Error
}

// GetByID retrieves a user by ID.
func (r *GormUserRepository) GetByID(userID string) (model.User, error) {
	var user model.User
	if err := r.DB.Where("user_id = ?", userID).First(&user).Error; err != nil {
		return user, err
	}
	return user, nil
}

// GetByUsername searches for a user by username.
func (r *GormUserRepository) GetByUsername(username string) (model.User, error) {
	var user model.User
	if err := r.DB.Where("username = ?", username).First(&user).Error; err != nil {
		return user, err
	}
	return user, nil
}
