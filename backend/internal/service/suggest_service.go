package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"skeleton-internship-backend/config"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/repository"
	"time"
)

type SuggestService interface {
	SuggestActivities(travelPreference *dto.TravelPreference) (*dto.ActivitiesSuggestion, error)
	SuggestRestaurants(travelPreference *dto.TravelPreference) (*dto.RestaurantSuggestion, error)
	SuggestAccommodations(travelPreference *dto.TravelPreference) (*dto.AccommodationSuggestion, error)
}

type suggestService struct {
	ActivityRepository      repository.ActivityRepository
	RestaurantRepository    repository.RestaurantRepository
	AccommodationRepository repository.AccommodationRepository
}

func NewSuggestService(
	activityRepo repository.ActivityRepository,
	restaurantRepo repository.RestaurantRepository,
	accommodationRepo repository.AccommodationRepository,
) SuggestService {
	return &suggestService{
		ActivityRepository:      activityRepo,
		RestaurantRepository:    restaurantRepo,
		AccommodationRepository: accommodationRepo,
	}
}

func (ss *suggestService) SuggestActivities(travelPreference *dto.TravelPreference) (*dto.ActivitiesSuggestion, error) {
	// Create HTTP client
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Prepare request body
	reqBody, err := json.Marshal(travelPreference)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal travel preference: %w", err)
	}

	// Create request to AI service
	aiURL := fmt.Sprintf("http://%s:%s/suggest/activities",
		config.AppConfig.AI.Host,
		config.AppConfig.AI.Port)

	req, err := http.NewRequest("POST", aiURL, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	// Send request
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request to AI service: %w", err)
	}
	defer resp.Body.Close()

	// Check response status
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("AI service returned non-200 status code: %d", resp.StatusCode)
	}

	// Read and parse response
	var rsp dto.TravelSuggestionResponse
	if err := json.NewDecoder(resp.Body).Decode(&rsp); err != nil {
		return nil, fmt.Errorf("failed to decode AI service response: %w", err)
	}

	var suggestion dto.ActivitiesSuggestion
	for i := range rsp.IDs {
		activities, err := ss.ActivityRepository.GetByID(rsp.IDs[i])
		if err != nil {
			return nil, fmt.Errorf("failed to fetch accommodation with ID %s: %w", rsp.IDs[i], err)
		}
		suggestion.Activities = append(suggestion.Activities, activities)
	}

	return &suggestion, nil
}

func (ss *suggestService) SuggestRestaurants(travelPreference *dto.TravelPreference) (*dto.RestaurantSuggestion, error) {
	// Create HTTP client
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Prepare request body
	reqBody, err := json.Marshal(travelPreference)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal travel preference: %w", err)
	}

	// Create request to AI service
	aiURL := fmt.Sprintf("http://%s:%s/suggest/restaurants",
		config.AppConfig.AI.Host,
		config.AppConfig.AI.Port)

	req, err := http.NewRequest("POST", aiURL, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	// Send request
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request to AI service: %w", err)
	}
	defer resp.Body.Close()

	// Check response status
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("AI service returned non-200 status code: %d", resp.StatusCode)
	}

	// Read and parse response
	var rsp dto.TravelSuggestionResponse
	if err := json.NewDecoder(resp.Body).Decode(&rsp); err != nil {
		return nil, fmt.Errorf("failed to decode AI service response: %w", err)
	}

	var suggestion dto.RestaurantSuggestion
	for i := range rsp.IDs {
		restaurant, err := ss.RestaurantRepository.GetByID(rsp.IDs[i])
		if err != nil {
			return nil, fmt.Errorf("failed to fetch accommodation with ID %s: %w", rsp.IDs[i], err)
		}
		suggestion.Restaurants = append(suggestion.Restaurants, restaurant)
	}

	return &suggestion, nil
}

func (ss *suggestService) SuggestAccommodations(travelPreference *dto.TravelPreference) (*dto.AccommodationSuggestion, error) {
	// Create HTTP client
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Prepare request body
	reqBody, err := json.Marshal(travelPreference)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal travel preference: %w", err)
	}

	// Create request to AI service
	aiURL := fmt.Sprintf("http://%s:%s/suggest/accommodations",
		config.AppConfig.AI.Host,
		config.AppConfig.AI.Port)

	req, err := http.NewRequest("POST", aiURL, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	// Send request
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request to AI service: %w", err)
	}
	defer resp.Body.Close()

	// Check response status
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("AI service returned non-200 status code: %d", resp.StatusCode)
	}

	// Read and parse response
	var rsp dto.TravelSuggestionResponse
	if err := json.NewDecoder(resp.Body).Decode(&rsp); err != nil {
		return nil, fmt.Errorf("failed to decode AI service response: %w", err)
	}

	var suggestion dto.AccommodationSuggestion
	for i := range rsp.IDs {
		accommodation, err := ss.AccommodationRepository.GetByID(rsp.IDs[i])
		if err != nil {
			return nil, fmt.Errorf("failed to fetch accommodation with ID %s: %w", rsp.IDs[i], err)
		}
		suggestion.Accommodations = append(suggestion.Accommodations, accommodation)
	}

	return &suggestion, nil
}
