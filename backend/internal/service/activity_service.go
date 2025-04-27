package service

import (
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"

	"github.com/google/uuid"
)

type ActivityService interface {
	CreateActivity(activity *model.Activity) (string, error)
	GetByID(id string) (model.Activity, error)
	GetWithCategory(id string) (model.Activity, error)
	GetByDestinationID(destinationID string) ([]model.Activity, error)
	GetByCategoryID(categoryID string) ([]model.Activity, error)
}

type activityService struct {
	activityRepo repository.ActivityRepository
}

func NewActivityService(
	activityRepo repository.ActivityRepository,
) ActivityService {
	return &activityService{
		activityRepo: activityRepo,
	}
}

func (s *activityService) CreateActivity(activity *model.Activity) (string, error) {
	// Generate UUID for activity
	activity.ActivityID = uuid.New().String()

	// Begin transaction
	tx := s.activityRepo.(*repository.GormActivityRepository).DB.Begin()

	// Create activity
	if err := tx.Create(activity).Error; err != nil {
		tx.Rollback()
		return "", err
	}

	// Commit transaction
	if err := tx.Commit().Error; err != nil {
		return "", err
	}
	return activity.ActivityID, nil
}

func (s *activityService) GetByID(id string) (model.Activity, error) {
	return s.activityRepo.GetByID(id)
}

func (s *activityService) GetWithCategory(id string) (model.Activity, error) {
	return s.activityRepo.GetWithCategory(id)
}

func (s *activityService) GetByDestinationID(destinationID string) ([]model.Activity, error) {
	return s.activityRepo.GetByDestinationID(destinationID)
}

func (s *activityService) GetByCategoryID(categoryID string) ([]model.Activity, error) {
	return s.activityRepo.GetByCategoryID(categoryID)
}
