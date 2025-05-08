package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// CommentRepository defines data access methods for the Comment entity.
type CommentRepository interface {
	GetByID(commentID string) (model.Comment, error)
	Create(comment *model.Comment) error
	Update(comment *model.Comment) error
	Delete(commentID string) error
	GetByActivityID(activityID string) ([]model.Comment, error)
	GetAll() ([]model.Comment, error)
	GetWithAssociations(commentID string) (model.Comment, error)
	GetAllWithAssociations() ([]model.Comment, error)
	GetByTripPlaceID(tripPlaceID string) ([]model.Comment, error)
	GetByTripRestaurantID(tripRestaurantID string) ([]model.Comment, error)
	GetByTripAccommodationID(tripAccommodationID string) ([]model.Comment, error)
}

// GormCommentRepository implements CommentRepository using GORM.
type GormCommentRepository struct {
	DB *gorm.DB
}

// NewCommentRepository returns a new GORM-based Comment repository.
func NewCommentRepository(db *gorm.DB) CommentRepository {
	return &GormCommentRepository{DB: db}
}

// GetByID retrieves a Comment by its ID.
func (r *GormCommentRepository) GetByID(commentID string) (model.Comment, error) {
	var comment model.Comment
	if err := r.DB.First(&comment, "comment_id = ?", commentID).Error; err != nil {
		return model.Comment{}, err
	}
	return comment, nil
}

// Create saves a new Comment record.
func (r *GormCommentRepository) Create(comment *model.Comment) error {
	return r.DB.Create(comment).Error
}

// Update modifies an existing Comment record.
func (r *GormCommentRepository) Update(comment *model.Comment) error {
	return r.DB.Model(&model.Comment{}).Where("comment_id = ?", comment.CommentID).Updates(comment).Error
}

// Delete removes a Comment record by its ID.
func (r *GormCommentRepository) Delete(commentID string) error {
	return r.DB.Delete(&model.Comment{}, "comment_id = ?", commentID).Error
}

// GetByActivityID retrieves all Comment records associated with a specific ActivityID.
func (r *GormCommentRepository) GetByActivityID(activityID string) ([]model.Comment, error) {
	var comments []model.Comment
	if err := r.DB.Where("trip_restaurant_id = ? OR trip_accommodation_id = ? OR trip_place_id = ?", activityID, activityID, activityID).Find(&comments).Error; err != nil {
		return nil, err
	}
	return comments, nil
}

// GetAll retrieves all Comment records.
func (r *GormCommentRepository) GetAll() ([]model.Comment, error) {
	var comments []model.Comment
	if err := r.DB.Find(&comments).Error; err != nil {
		return nil, err
	}
	return comments, nil
}

// GetWithAssociations retrieves a Comment by its ID with associated records.
func (r *GormCommentRepository) GetWithAssociations(commentID string) (model.Comment, error) {
	var comment model.Comment
	if err := r.DB.Preload("TripRestaurantID").Preload("TripAccommodationID").Preload("TripPlaceID").First(&comment, "comment_id = ?", commentID).Error; err != nil {
		return comment, err
	}
	return comment, nil
}

// GetAllWithAssociations retrieves all Comment records with associated records.
func (r *GormCommentRepository) GetAllWithAssociations() ([]model.Comment, error) {
	var comments []model.Comment
	if err := r.DB.Preload("TripRestaurantID").Preload("TripAccommodationID").Preload("TripPlaceID").Find(&comments).Error; err != nil {
		return nil, err
	}
	return comments, nil
}

// GetByTripPlaceID retrieves all comments associated with a specific TripPlaceID.
func (r *GormCommentRepository) GetByTripPlaceID(tripPlaceID string) ([]model.Comment, error) {
	var comments []model.Comment
	if err := r.DB.Where("trip_place_id = ?", tripPlaceID).Find(&comments).Error; err != nil {
		return nil, err
	}
	return comments, nil
}

// GetByTripRestaurantID retrieves all comments associated with a specific TripRestaurantID.
func (r *GormCommentRepository) GetByTripRestaurantID(tripRestaurantID string) ([]model.Comment, error) {
	var comments []model.Comment
	if err := r.DB.Where("trip_restaurant_id = ?", tripRestaurantID).Find(&comments).Error; err != nil {
		return nil, err
	}
	return comments, nil
}

// GetByTripAccommodationID retrieves all comments associated with a specific TripAccommodationID.
func (r *GormCommentRepository) GetByTripAccommodationID(tripAccommodationID string) ([]model.Comment, error) {
	var comments []model.Comment
	if err := r.DB.Where("trip_accommodation_id = ?", tripAccommodationID).Find(&comments).Error; err != nil {
		return nil, err
	}
	return comments, nil
}
