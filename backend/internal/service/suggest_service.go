package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"skeleton-internship-backend/config"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"
	"time"
)

type SuggestService interface {
	SuggestPlaces(travelPreference *model.TravelPreference) (*dto.PlacesSuggestion, error)
	SuggestRestaurants(travelPreference *model.TravelPreference) (*dto.RestaurantsSuggestion, error)
	SuggestAccommodations(travelPreference *model.TravelPreference) (*dto.AccommodationsSuggestion, error)
	SuggestAll(travelPreference *model.TravelPreference) (*dto.TripSuggestionRequest, error)
	GetPlaceByID(id string) (model.Place, error)
	GetRestaurantByID(id string) (model.Restaurant, error)
	GetAccommodationByID(id string) (model.Accommodation, error)
	SuggestWithComment(req *dto.SuggestWithCommentRequest) (*dto.SuggestWithCommentResponse, error)
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
func (ss *suggestService) callAISuggestion(endpoint string, travelPreference *model.TravelPreference) (*dto.TravelSuggestionResponse, error) {
	client := &http.Client{
		Timeout: 10000 * time.Second,
	}

	var jsonBody bytes.Buffer
	if err := json.NewEncoder(&jsonBody).Encode(travelPreference); err != nil {
		return nil, fmt.Errorf("failed to encode travel preference to JSON: %w", err)
	}

	aiURL := fmt.Sprintf("http://%s:%s%s",
		config.AppConfig.AI.Host,
		config.AppConfig.AI.Port,
		endpoint,
	)

	req, err := http.NewRequest("GET", aiURL, &jsonBody)
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

func (ss *suggestService) mockCallSuggestAccommodationAPI(endpoint string, travelPreference *model.TravelPreference) (*dto.TravelSuggestionResponse, error) {
	fmt.Println("Mock API call to:", endpoint)
	fmt.Println("Travel Preference:", travelPreference)

	return &dto.TravelSuggestionResponse{
		IDs: []string{"accom_000001", "accom_000002", "accom_000003"},
	}, nil
}

func (ss *suggestService) mockCallSuggestPlaceAPI(endpoint string, travelPreference *model.TravelPreference) (*dto.TravelSuggestionResponse, error) {
	fmt.Println("Mock API call to:", endpoint)
	fmt.Println("Travel Preference:", travelPreference)

	return &dto.TravelSuggestionResponse{
		IDs: []string{"act_000001", "act_000002", "act_000003"},
	}, nil
}

func (ss *suggestService) mockCallSuggestRestaurantAPI(endpoint string, travelPreference *model.TravelPreference) (*dto.TravelSuggestionResponse, error) {
	fmt.Println("Mock API call to:", endpoint)
	fmt.Println("Travel Preference:", travelPreference)

	return &dto.TravelSuggestionResponse{
		IDs: []string{"rest_000001", "rest_000002"},
	}, nil
}

func getURL(host, port, endpoint string) string {
	return fmt.Sprintf("http://%s:%s%s", host, port, endpoint)
}

func (ss *suggestService) SuggestAccommodations(travelPreference *model.TravelPreference) (*dto.AccommodationsSuggestion, error) {
	rsp, err := ss.mockCallSuggestAccommodationAPI(
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

func (ss *suggestService) SuggestPlaces(travelPreference *model.TravelPreference) (*dto.PlacesSuggestion, error) {
	rsp, err := ss.mockCallSuggestPlaceAPI(
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
			Images:        place.Images,
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

func (ss *suggestService) SuggestRestaurants(travelPreference *model.TravelPreference) (*dto.RestaurantsSuggestion, error) {
	rsp, err := ss.mockCallSuggestRestaurantAPI(
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
			RestaurantID:  restaurant.RestaurantID,
			DestinationID: restaurant.DestinationID,
			Name:          restaurant.Name,
			Address:       restaurant.Address,
			Rating:        restaurant.Rating,
			Phone:         restaurant.Phone,
			PhotoURL:      restaurant.PhotoURL,
			URL:           restaurant.URL,
			Location:      restaurant.Location,
			Reviews:       restaurant.Reviews,
			Services:      restaurant.Services,
			IsDelivery:    restaurant.IsDelivery,
			IsBooking:     restaurant.IsBooking,
			IsOpening:     restaurant.IsOpening,
			PriceRange:    restaurant.PriceRange,
			Description:   restaurant.Description,
			Cuisines:      restaurant.Cuisines,
			OpeningHours:  restaurant.OpeningHours,
		}
		suggestion.Restaurants = append(suggestion.Restaurants, suggestedRestaurant)
	}
	return &suggestion, nil
}

func (ss *suggestService) callAISuggestAll(endpoint string, travelPreference *model.TravelPreference) ([]dto.SuggestWithIDAndType, error) {
	client := &http.Client{
		Timeout: 10000 * time.Second,
	}
	var jsonBody bytes.Buffer
	if err := json.NewEncoder(&jsonBody).Encode(travelPreference); err != nil {
		return nil, fmt.Errorf("failed to encode travel preference to JSON: %w", err)
	}
	aiURL := fmt.Sprintf("http://%s:%s%s",
		config.AppConfig.AI.Host,
		config.AppConfig.AI.Port,
		endpoint,
	)

	req, err := http.NewRequest("POST", aiURL, &jsonBody)
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

	var rsp []dto.SuggestWithIDAndType
	if err := json.NewDecoder(resp.Body).Decode(&rsp); err != nil {
		return nil, fmt.Errorf("failed to decode AI service response: %w", err)
	}
	return rsp, nil
}

func (ss *suggestService) SuggestAll(travelPreference *model.TravelPreference) (*dto.TripSuggestionRequest, error) {
	// rsp, err := ss.callAISuggestAll(
	// 	"/api/v1/suggest/all",
	// 	travelPreference,
	// )
	// if err != nil {
	// 	return nil, err
	// }

	var err error
	var rsp []dto.SuggestWithIDAndType
	rsp = append(rsp,
		dto.SuggestWithIDAndType{
			Name: "hotel_000000",
			Type: "accommodation",
			Args: "...",
			ID:   "hotel_000000",
		},
		dto.SuggestWithIDAndType{
			Name: "restaurant_000000",
			Type: "restaurant",
			Args: "...",
			ID:   "restaurant_000000",
		},
		dto.SuggestWithIDAndType{
			Name: "place_000000",
			Type: "place",
			Args: "...",
			ID:   "place_000000",
		},
	)
	data, err := json.MarshalIndent(rsp, "", "  ")
	if err != nil {
		fmt.Println("Error converting mockdata to json:", err)
	} else {
		fmt.Println("mockdata in JSON:", string(data))
	}

	var suggestion *dto.TripSuggestionRequest
	suggestion, err = ss.ConvertIntoTripSuggestion(rsp)
	if err != nil {
		return nil, err
	}
	// fmt.Println("Converted suggestion: ", suggestion)

	return suggestion, nil
}

func (ss *suggestService) ConvertIntoTripSuggestion(suggests []dto.SuggestWithIDAndType) (*dto.TripSuggestionRequest, error) {
	var tripSuggestion dto.TripSuggestionRequest
	var accommodations dto.AccommodationsSuggestion
	var places dto.PlacesSuggestion
	var restaurants dto.RestaurantsSuggestion
	for _, value := range suggests {
		if value.Type == "accommodation" {
			newAccommodation, err := ss.AccommodationRepository.GetByID(value.ID)
			if err != nil {
				fmt.Println("Error fetching accommodation: ", value.ID)
				// return nil, err
				continue
			}
			accommodations.Accommodations = append(
				accommodations.Accommodations,
				dto.AccommodationSuggestion{
					AccommodationID: newAccommodation.AccommodationID,
					DestinationID:   newAccommodation.DestinationID,
					Name:            newAccommodation.Name,
					Location:        newAccommodation.Location,
					City:            newAccommodation.City,
					Price:           newAccommodation.Price,
					Rating:          newAccommodation.Rating,
					Description:     newAccommodation.Description,
					Link:            newAccommodation.Link,
					Images:          newAccommodation.Images,
					RoomTypes:       newAccommodation.RoomTypes,
					RoomInfo:        newAccommodation.RoomInfo,
					Unit:            newAccommodation.Unit,
					TaxInfo:         newAccommodation.TaxInfo,
					ElderlyFriendly: newAccommodation.ElderlyFriendly,
				},
			)
		}
		if value.Type == "place" {
			newPlace, err := ss.PlaceRepository.GetByID(value.ID)
			if err != nil {
				fmt.Println("Error fetching place: ", value.ID)
				// return nil, err
				continue
			}
			places.Places = append(
				places.Places,
				dto.PlaceSuggestion{
					PlaceID:       newPlace.PlaceID,
					DestinationID: newPlace.DestinationID,
					Name:          newPlace.Name,
					URL:           newPlace.URL,
					Address:       newPlace.Address,
					Duration:      newPlace.Duration,
					Type:          newPlace.Type,
					Images:        newPlace.Images,
					MainImage:     newPlace.MainImage,
					Price:         newPlace.Price,
					Rating:        newPlace.Rating,
					Description:   newPlace.Description,
					OpeningHours:  newPlace.OpeningHours,
					Reviews:       newPlace.Reviews,
					Categories:    newPlace.Categories,
					Unit:          newPlace.Unit,
				},
			)
		}
		if value.Type == "restaurant" {
			newRestaurant, err := ss.RestaurantRepository.GetByID(value.ID)
			if err != nil {
				fmt.Println("Error fetching restaurant: ", value.ID)
				// return nil, err
				continue
			}
			restaurants.Restaurants = append(
				restaurants.Restaurants,
				dto.RestaurantSuggestion{
					RestaurantID:  newRestaurant.RestaurantID,
					DestinationID: newRestaurant.DestinationID,
					Name:          newRestaurant.Name,
					Address:       newRestaurant.Address,
					Rating:        newRestaurant.Rating,
					Phone:         newRestaurant.Phone,
					PhotoURL:      newRestaurant.PhotoURL,
					URL:           newRestaurant.URL,
					Location:      newRestaurant.Location,
					Reviews:       newRestaurant.Reviews,
					Services:      newRestaurant.Services,
					IsDelivery:    newRestaurant.IsDelivery,
					IsBooking:     newRestaurant.IsBooking,
					IsOpening:     newRestaurant.IsOpening,
					PriceRange:    newRestaurant.PriceRange,
					Description:   newRestaurant.Description,
					Cuisines:      newRestaurant.Cuisines,
					OpeningHours:  newRestaurant.OpeningHours,
				},
			)
		}
	}
	tripSuggestion.Accommodation = accommodations
	tripSuggestion.Places = places
	tripSuggestion.Restaurants = restaurants
	return &tripSuggestion, nil
}

func (ss *suggestService) GetPlaceByID(id string) (model.Place, error) {
	place, err := ss.PlaceRepository.GetByID(id)
	if err != nil {
		return model.Place{}, err
	}
	return place, nil
}

func (ss *suggestService) GetRestaurantByID(id string) (model.Restaurant, error) {
	restaurant, err := ss.RestaurantRepository.GetByID(id)
	if err != nil {
		return model.Restaurant{}, err
	}
	return restaurant, nil
}

func (ss *suggestService) GetAccommodationByID(id string) (model.Accommodation, error) {
	accommodation, err := ss.AccommodationRepository.GetByID(id)
	if err != nil {
		return model.Accommodation{}, err
	}
	return accommodation, nil
}

// callAISuggestWithComment now returns the raw JSON response from the AI service.
func (ss *suggestService) callAISuggestWithComment(req *dto.SuggestWithCommentRequest) ([]byte, error) {
	client := &http.Client{
		Timeout: 10000 * time.Second,
	}

	var jsonBody bytes.Buffer
	if err := json.NewEncoder(&jsonBody).Encode(req); err != nil {
		return nil, fmt.Errorf("failed to encode suggest with comment request to JSON: %w", err)
	}

	aiURL := fmt.Sprintf("http://%s:%s%s",
		config.AppConfig.AI.Host,
		config.AppConfig.AI.Port,
		"/suggest/comment",
	)

	httpReq, err := http.NewRequest("POST", aiURL, &jsonBody)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("failed to send request to AI service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("AI service returned non-200 status code: %d", resp.StatusCode)
	}

	// Read and return the raw JSON response.
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read AI service response body: %w", err)
	}
	return body, nil
}

// SuggestWithComment calls the AI service for comment-based suggestions,
// receives the JSON response, parses it into SuggestWithCommentResponse and returns it.
func (ss *suggestService) SuggestWithComment(req *dto.SuggestWithCommentRequest) (*dto.SuggestWithCommentResponse, error) {
	jsonResponse, err := ss.callAISuggestWithComment(req)
	// jsonResponse, err := ss.mockCallSuggestWithCommentAPI(req)
	if err != nil {
		return nil, err
	}

	var aiResponse dto.SuggestWithCommentResponse
	if err := json.Unmarshal(jsonResponse, &aiResponse); err != nil {
		return nil, fmt.Errorf("failed to decode AI service response: %w", err)
	}
	return &aiResponse, nil
}

// mockCallSuggestWithCommentAPI provides mock JSON data for the comment-based suggestion API.
func (ss *suggestService) mockCallSuggestWithCommentAPI(req *dto.SuggestWithCommentRequest) ([]byte, error) {
	mockJSON := `
	{
  "suggestion_type": "restaurant",
  "suggestion_ids": [
    "restaurant_001440",
    "restaurant_000280",
    "restaurant_000424",
    "restaurant_000040",
    "restaurant_001247",
    "restaurant_000769",
    "restaurant_000712",
    "restaurant_000193",
    "restaurant_000631",
    "restaurant_000149"
  ]
}
`
	return []byte(mockJSON), nil
}
