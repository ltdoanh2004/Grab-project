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
	SuggestRestaurants(travelPreference *dto.TravelPreference) (*dto.RestaurantsSuggestion, error)
	SuggestAccommodations(travelPreference *dto.TravelPreference) (*dto.AccommodationsSuggestion, error)
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

// callAISuggestion handles the common API call to the AI service.
func (ss *suggestService) callAISuggestion(endpoint string, travelPreference *dto.TravelPreference) (*dto.TravelSuggestionResponse, error) {
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	reqBody, err := json.Marshal(travelPreference)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal travel preference: %w", err)
	}

	aiURL := fmt.Sprintf("http://%s:%s%s",
		config.AppConfig.AI.Host,
		config.AppConfig.AI.Port,
		endpoint,
	)

	req, err := http.NewRequest("POST", aiURL, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request to AI service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("AI service returned non-200 status code: %d", resp.StatusCode)
	}

	var rsp dto.TravelSuggestionResponse
	if err := json.NewDecoder(resp.Body).Decode(&rsp); err != nil {
		return nil, fmt.Errorf("failed to decode AI service response: %w", err)
	}
	return &rsp, nil
}

func (ss *suggestService) mockCallAPI(endpoint string, travelPreference *dto.TravelPreference) (*dto.TravelSuggestionResponse, error) {
	fmt.Println("Mock API call to:", endpoint)
	fmt.Println("Travel Preference:", travelPreference)

	return &dto.TravelSuggestionResponse{
		IDs: []string{"hotel_000001", "hotel_000002", "hotel_000003"},
	}, nil
}

func getURL(host, port, endpoint string) string {
	return fmt.Sprintf("http://%s:%s%s", host, port, endpoint)
}

func (ss *suggestService) SuggestAccommodations(travelPreference *dto.TravelPreference) (*dto.AccommodationsSuggestion, error) {
	rsp, err := ss.mockCallAPI(
		getURL(config.AppConfig.AI.Host,
			config.AppConfig.AI.Port,
			"/suggest/accommodations",
		),
		travelPreference,
	)
	if err != nil {
		return nil, err
	}

	var suggestion dto.AccommodationsSuggestion
	for i := range rsp.IDs {
		accommodation, err := ss.AccommodationRepository.GetByID(rsp.IDs[i])
		if err != nil {
			return nil, fmt.Errorf("failed to fetch accommodation with ID %s: %w", rsp.IDs[i], err)
		}
		suggestedAccommodation := dto.AccommodationSuggestion{
			AccommodationID: accommodation.AccommodationID,
			DestinationID:   accommodation.DestinationID,
			Name:            accommodation.Name,
			Type:            accommodation.Type,
			Address:         accommodation.Address,
			BookingLink:     accommodation.BookingLink,
			StarRating:      accommodation.StarRating,
			Description:     accommodation.Description,
			Amenities:       accommodation.Amenities,
			ImageURL:        accommodation.ImageURL,
		}

		suggestion.Accommodations = append(suggestion.Accommodations, suggestedAccommodation)
	}
	return &suggestion, nil
}

func (ss *suggestService) SuggestActivities(travelPreference *dto.TravelPreference) (*dto.ActivitiesSuggestion, error) {
	rsp, err := ss.callAISuggestion(
		getURL(config.AppConfig.AI.Host,
			config.AppConfig.AI.Port,
			"/suggest/activities",
		),
		travelPreference,
	)
	if err != nil {
		return nil, err
	}

	var suggestion dto.ActivitiesSuggestion
	for i := range rsp.IDs {
		activity, err := ss.ActivityRepository.GetByID(rsp.IDs[i])
		if err != nil {
			return nil, fmt.Errorf("failed to fetch activity with ID %s: %w", rsp.IDs[i], err)
		}
		suggestedActivity := dto.ActivitySuggestion{
			ActivityID:    activity.ActivityID,
			DestinationID: activity.DestinationID,
			CategoryID:    activity.CategoryID,
			Name:          activity.Name,
			Description:   activity.Description,
			Duration:      activity.Duration,
			Cost:          activity.Cost,
			ImageURL:      activity.ImageURL,
			PlaceID:       activity.PlaceID,
		}
		suggestion.Activities = append(suggestion.Activities, suggestedActivity)
	}
	return &suggestion, nil
}

func (ss *suggestService) SuggestRestaurants(travelPreference *dto.TravelPreference) (*dto.RestaurantsSuggestion, error) {
	rsp, err := ss.callAISuggestion(
		getURL(config.AppConfig.AI.Host,
			config.AppConfig.AI.Port,
			"/suggest/restaurants",
		),
		travelPreference,
	)
	if err != nil {
		return nil, err
	}

	var suggestion dto.RestaurantsSuggestion
	for i := range rsp.IDs {
		restaurant, err := ss.RestaurantRepository.GetByID(rsp.IDs[i])
		if err != nil {
			return nil, fmt.Errorf("failed to fetch restaurant with ID %s: %w", rsp.IDs[i], err)
		}
		suggestedRestaurant := dto.RestaurantSuggestion{
			RestaurantID:      restaurant.RestaurantID,
			DestinationID:     restaurant.DestinationID,
			Name:              restaurant.Name,
			EstablishmentType: restaurant.EstablishmentType,
			CuisineType:       restaurant.CuisineType,
			Description:       restaurant.Description,
			Address:           restaurant.Address,
			PriceRange:        restaurant.PriceRange,
			AvgRating:         restaurant.AvgRating,
			OpeningHours:      restaurant.OpeningHours,
			ImageURL:          restaurant.ImageURL,
		}
		suggestion.Restaurants = append(suggestion.Restaurants, suggestedRestaurant)
	}
	return &suggestion, nil
}
