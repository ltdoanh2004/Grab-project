package service

import (
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"

	"github.com/google/uuid"
)

type CommentService interface {
	AddComment(comment *model.Comment) (string, error)
	GetComment(commentID string) (model.Comment, error)
	GetCommentsByTripID(tripID string) ([]model.Comment, error)
	GetCommentsByActivity(activity dto.Activity) ([]model.Comment, error)
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

func (ts *commentService) AddComment(comment *model.Comment) (string, error) {
	commentID := uuid.New().String()
	comment.CommentID = commentID

	// Create the main comment record
	if err := ts.commentRepository.Create(comment); err != nil {
		return "", err
	}

	return commentID, nil
}

func (ts *commentService) GetComment(commentID string) (model.Comment, error) {
	return ts.commentRepository.GetByID(commentID)
}

func (ts *commentService) GetCommentsByTripID(tripID string) ([]model.Comment, error) {
	return ts.commentRepository.GetByTripID(tripID)
}

func (ts *commentService) GetCommentsByActivity(activity dto.Activity) ([]model.Comment, error) {
	if activity.Type == "place" {
		return ts.commentRepository.GetByTripPlaceID(activity.ActivityID)
	}
	if activity.Type == "restaurant" {
		return ts.commentRepository.GetByTripRestaurantID(activity.ActivityID)
	}
	return ts.commentRepository.GetByTripAccommodationID(activity.ActivityID)
}
