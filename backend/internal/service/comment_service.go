package service

import (
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"

	"github.com/google/uuid"
)

type CommentService interface {
	AddComment(comment *dto.Comment, userID string) (string, error)
	GetComment(commentID string) (model.Comment, error)
	GetCommentsByActivityID(activityID string) ([]model.Comment, error)
}

type commentService struct {
	commentRepository repository.CommentRepository
}

func NewCommentService(
	commentRepo repository.CommentRepository,
) CommentService {
	return &commentService{
		commentRepository: commentRepo,
	}
}

func (ts *commentService) AddComment(comment *dto.Comment, userID string) (string, error) {
	commentID := uuid.New().String()
	commentEntity := &model.Comment{
		CommentID:      commentID,
		UserID:         userID,
		CommentMessage: comment.CommentMessage,
	}

	if comment.Type == "place" {
		commentEntity.TripPlaceID = &comment.ActivityID
	} else if comment.Type == "restaurant" {
		commentEntity.TripRestaurantID = &comment.ActivityID
	} else if comment.Type == "accommodation" {
		commentEntity.TripAccommodationID = &comment.ActivityID
	}

	// Create the main comment record
	if err := ts.commentRepository.Create(commentEntity); err != nil {
		return "", err
	}

	return commentID, nil
}

func (ts *commentService) GetComment(commentID string) (model.Comment, error) {
	return ts.commentRepository.GetByID(commentID)
}

func (ts *commentService) GetCommentsByActivityID(activityID string) ([]model.Comment, error) {
	return ts.commentRepository.GetByActivityID(activityID)
}
