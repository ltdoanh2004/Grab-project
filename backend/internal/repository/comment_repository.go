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
	GetByTripID(tripID string) ([]model.Comment, error)
	GetAll() ([]model.Comment, error)
	GetWithAssociations(commentID string) (model.Comment, error)
	GetAllWithAssociations() ([]model.Comment, error)
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

// GetByTripID retrieves all Comment records associated with a specific TripID.
func (r *GormCommentRepository) GetByTripID(tripID string) ([]model.Comment, error) {
	var comments []model.Comment
	if err := r.DB.Where("trip_restaurant_id = ? OR trip_accommodation_id = ? OR trip_place_id = ?", tripID, tripID, tripID).Find(&comments).Error; err != nil {
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
