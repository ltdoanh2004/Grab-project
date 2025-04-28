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
	SuggestPlaces(travelPreference *dto.TravelPreference) (*dto.PlacesSuggestion, error)
	SuggestRestaurants(travelPreference *dto.TravelPreference) (*dto.RestaurantsSuggestion, error)
	SuggestAccommodations(travelPreference *dto.TravelPreference) (*dto.AccommodationsSuggestion, error)
}

type suggestService struct {
	PlaceRepository         repository.PlaceRepository
	RestaurantRepository    repository.RestaurantRepository
	AccommodationRepository repository.AccommodationRepository
}

func NewSuggestService(
	placeRepo repository.PlaceRepository,
	restaurantRepo repository.RestaurantRepository,
	accommodationRepo repository.AccommodationRepository,
) SuggestService {
	return &suggestService{
		PlaceRepository:         placeRepo,
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
		accommodation, err := ss.AccommodationRepository.GetByIDWithAssociations(rsp.IDs[i])
		if err != nil {
			return nil, fmt.Errorf("failed to fetch accommodation with ID %s: %w", rsp.IDs[i], err)
		}
		suggestedAccommodation := dto.AccommodationSuggestion{
			AccommodationID: accommodation.AccommodationID,
			DestinationID:   accommodation.DestinationID,
			Name:            accommodation.Name,
			Location:        accommodation.Location,
			City:            accommodation.City,
			Price:           accommodation.Price,
			Rating:          accommodation.Rating,
			Description:     accommodation.Description,
			Link:            accommodation.Link,
			Images:          accommodation.Images,
			RoomTypes:       accommodation.RoomTypes,
			RoomInfo:        accommodation.RoomInfo,
			Unit:            accommodation.Unit,
			TaxInfo:         accommodation.TaxInfo,
			ElderlyFriendly: accommodation.ElderlyFriendly,
		}

		suggestion.Accommodations = append(suggestion.Accommodations, suggestedAccommodation)
	}
	return &suggestion, nil
}

func (ss *suggestService) SuggestPlaces(travelPreference *dto.TravelPreference) (*dto.PlacesSuggestion, error) {
	rsp, err := ss.callAISuggestion(
		getURL(config.AppConfig.AI.Host,
			config.AppConfig.AI.Port,
			"/suggest/places",
		),
		travelPreference,
	)
	if err != nil {
		return nil, err
	}

	var suggestion dto.PlacesSuggestion
	for i := range rsp.IDs {
		place, err := ss.PlaceRepository.GetByID(rsp.IDs[i])
		if err != nil {
			return nil, fmt.Errorf("failed to fetch place with ID %s: %w", rsp.IDs[i], err)
		}
		suggestedPlace := dto.PlaceSuggestion{
			PlaceID:       place.PlaceID,
			DestinationID: place.DestinationID,
			Name:          place.Name,
			URL:           place.URL,
			Address:       place.Address,
			Duration:      place.Duration,
			Type:          place.Type,
			Categories:    place.Categories,
			ImageURLs:     place.ImageURLs,
			MainImage:     place.MainImage,
			Price:         place.Price,
			Rating:        place.Rating,
			Description:   place.Description,
			OpeningHours:  place.OpeningHours,
			Reviews:       place.Reviews,
		}
		suggestion.Places = append(suggestion.Places, suggestedPlace)
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
