package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"skeleton-internship-backend/config"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"
	"time"

	"github.com/google/uuid"
)

type TripService interface {
	CreateTrip(trip *dto.CreateTripRequest) (string, error)
	SaveTrip(trip *dto.TripDTO) error
	GetTrip(tripID string) (*dto.TripDTO, error)
	SuggestTrip(activities dto.TripSuggestionRequest, endpoint string) (*dto.CreateTripRequestByDate, error)
}

type tripService struct {
	tripRepository              repository.TripRepository
	tripDestinationRepository   repository.TripDestinationRepository
	tripAccommodationRepository repository.TripAccommodationRepository
	tripPlaceRepository         repository.TripPlaceRepository
	tripRestaurantRepository    repository.TripRestaurantRepository
}

func NewTripService(
	tripRepo repository.TripRepository,
	tripDestinationRepo repository.TripDestinationRepository,
	accommodationRepo repository.TripAccommodationRepository,
	placeRepo repository.TripPlaceRepository,
	restaurantRepo repository.TripRestaurantRepository,
) TripService {
	return &tripService{
		tripRepository:              tripRepo,
		tripDestinationRepository:   tripDestinationRepo,
		tripAccommodationRepository: accommodationRepo,
		tripPlaceRepository:         placeRepo,
		tripRestaurantRepository:    restaurantRepo,
	}
}

func (ts *tripService) CreateTrip(trip *dto.CreateTripRequest) (string, error) {
	tripID := uuid.New().String()

	// Create Trip entity
	tripEntity := &model.Trip{
		TripID:     tripID,
		UserID:     trip.UserID,
		TripName:   trip.TripName,
		StartDate:  trip.StartDate,
		EndDate:    trip.EndDate,
		Budget:     trip.Budget,
		TripStatus: trip.TripStatus,
	}

	// Create the main trip record
	if err := ts.tripRepository.Create(tripEntity); err != nil {
		return "", err
	}

	// Process each destination and its associated data
	for _, destReq := range trip.TripDestinations {
		// Create TripDestination
		destID := uuid.New().String()
		tripDest := &model.TripDestination{
			TripDestinationID: destID,
			TripID:            tripID,
			DestinationID:     destReq.DestinationID,
			ArrivalDate:       destReq.ArrivalDate,
			DepartureDate:     destReq.DepartureDate,
			OrderNum:          destReq.OrderNum,
		}

		if err := ts.tripDestinationRepository.Create(tripDest); err != nil {
			return "", err
		}

		// Process accommodations
		for _, acc := range destReq.Accommodations {
			tripAccom := &model.TripAccommodation{
				TripAccommodationID: uuid.New().String(),
				TripDestinationID:   destID,
				AccommodationID:     acc.AccommodationID,
				CheckInDate:         acc.CheckInDate,
				CheckOutDate:        acc.CheckOutDate,
				Cost:                acc.Cost,
				Notes:               acc.Notes,
			}
			if err := ts.tripAccommodationRepository.Create(tripAccom); err != nil {
				return "", err
			}
		}

		// Process places
		for _, act := range destReq.Places {
			tripAct := &model.TripPlace{
				TripPlaceID:       uuid.New().String(),
				TripDestinationID: destID,
				PlaceID:           act.PlaceID,
				ScheduledDate:     act.ScheduledDate,
				StartTime:         act.StartTime,
				EndTime:           act.EndTime,
				Notes:             act.Notes,
			}
			if err := ts.tripPlaceRepository.Create(tripAct); err != nil {
				return "", err
			}
		}

		// Process restaurants
		for _, rest := range destReq.Restaurants {
			tripRest := &model.TripRestaurant{
				TripRestaurantID:  uuid.New().String(),
				TripDestinationID: destID,
				RestaurantID:      rest.RestaurantID,
				MealDate:          rest.MealDate,
				StartTime:         rest.StartTime,
				EndTime:           rest.EndTime,
				ReservationInfo:   rest.ReservationInfo,
				Notes:             rest.Notes,
			}
			if err := ts.tripRestaurantRepository.Create(tripRest); err != nil {
				return "", err
			}
		}
	}

	return tripID, nil
}

func (ts *tripService) SaveTrip(trip *dto.TripDTO) error {
	// Update main trip record
	tripEntity := &model.Trip{
		TripID:     trip.TripID,
		UserID:     trip.UserID,
		TripName:   trip.TripName,
		StartDate:  trip.StartDate,
		EndDate:    trip.EndDate,
		Budget:     trip.Budget,
		TripStatus: trip.TripStatus,
	}

	if err := ts.tripRepository.Update(tripEntity); err != nil {
		return err
	}

	// Get existing destinations to compare
	existingDests, err := ts.tripDestinationRepository.GetByTripID(trip.TripID)
	if err != nil {
		return err
	}

	// Create a map of existing destinations for easy lookup
	existingDestMap := make(map[string]bool)
	for _, dest := range existingDests {
		existingDestMap[dest.TripDestinationID] = true
	}

	// Process destinations
	for _, destDTO := range trip.TripDestinations {
		tripDest := &model.TripDestination{
			TripDestinationID: destDTO.TripDestinationID,
			TripID:            trip.TripID,
			DestinationID:     destDTO.DestinationID,
			ArrivalDate:       destDTO.ArrivalDate,
			DepartureDate:     destDTO.DepartureDate,
			OrderNum:          destDTO.OrderNum,
		}

		if existingDestMap[destDTO.TripDestinationID] {
			// Update existing destination
			if err := ts.tripDestinationRepository.Update(tripDest); err != nil {
				return err
			}
		} else {
			// Create new destination
			if err := ts.tripDestinationRepository.Create(tripDest); err != nil {
				return err
			}
		}

		// Update accommodations
		for _, acc := range destDTO.Accommodations {
			tripAccom := &model.TripAccommodation{
				TripAccommodationID: acc.TripAccommodationID,
				TripDestinationID:   destDTO.TripDestinationID,
				AccommodationID:     acc.AccommodationID,
				CheckInDate:         acc.CheckInDate,
				CheckOutDate:        acc.CheckOutDate,
				Cost:                acc.Cost,
				Notes:               acc.Notes,
			}

			if acc.TripAccommodationID != "" {
				if err := ts.tripAccommodationRepository.Update(tripAccom); err != nil {
					return err
				}
			} else {
				if err := ts.tripAccommodationRepository.Create(tripAccom); err != nil {
					return err
				}
			}
		}

		// Update places
		for _, act := range destDTO.Places {
			tripAct := &model.TripPlace{
				TripPlaceID:       act.TripPlaceID,
				TripDestinationID: destDTO.TripDestinationID,
				PlaceID:           act.PlaceID,
				ScheduledDate:     act.ScheduledDate,
				StartTime:         act.StartTime,
				EndTime:           act.EndTime,
				Notes:             act.Notes,
			}

			if act.TripPlaceID != "" {
				if err := ts.tripPlaceRepository.Update(tripAct); err != nil {
					return err
				}
			} else {
				if err := ts.tripPlaceRepository.Create(tripAct); err != nil {
					return err
				}
			}
		}

		// Update restaurants
		for _, rest := range destDTO.Restaurants {
			tripRest := &model.TripRestaurant{
				TripRestaurantID:  rest.TripRestaurantID,
				TripDestinationID: destDTO.TripDestinationID,
				RestaurantID:      rest.RestaurantID,
				MealDate:          rest.MealDate,
				StartTime:         rest.StartTime,
				EndTime:           rest.EndTime,
				ReservationInfo:   rest.ReservationInfo,
				Notes:             rest.Notes,
			}

			if rest.TripRestaurantID != "" {
				if err := ts.tripRestaurantRepository.Update(tripRest); err != nil {
					return err
				}
			} else {
				if err := ts.tripRestaurantRepository.Create(tripRest); err != nil {
					return err
				}
			}
		}
	}

	return nil
}

func (ts *tripService) GetTrip(tripID string) (*dto.TripDTO, error) {
	// Get trip with all associations
	trip, err := ts.tripRepository.GetWithAssociations(tripID)
	if err != nil {
		return nil, err
	}

	// Get all destinations for this trip
	destinations, err := ts.tripDestinationRepository.GetByTripID(tripID)
	if err != nil {
		return nil, err
	}

	tripDTO := &dto.TripDTO{
		TripID:     trip.TripID,
		UserID:     trip.UserID,
		TripName:   trip.TripName,
		StartDate:  trip.StartDate,
		EndDate:    trip.EndDate,
		Budget:     trip.Budget,
		TripStatus: trip.TripStatus,
	}

	// Process each destination
	for _, dest := range destinations {
		destDTO := dto.TripDestinationDTO{
			TripDestinationID: dest.TripDestinationID,
			TripID:            dest.TripID,
			DestinationID:     dest.DestinationID,
			ArrivalDate:       dest.ArrivalDate,
			DepartureDate:     dest.DepartureDate,
			OrderNum:          dest.OrderNum,
		}

		// Get accommodations for this destination
		accommodations, err := ts.tripAccommodationRepository.GetByTripID(dest.TripDestinationID)
		if err != nil {
			return nil, err
		}

		for _, acc := range accommodations {
			destDTO.Accommodations = append(destDTO.Accommodations, dto.TripAccommodationDTO{
				TripAccommodationID: acc.TripAccommodationID,
				TripDestinationID:   acc.TripDestinationID,
				AccommodationID:     acc.AccommodationID,
				CheckInDate:         acc.CheckInDate,
				CheckOutDate:        acc.CheckOutDate,
				Cost:                acc.Cost,
				Notes:               acc.Notes,
			})
		}

		// Get places for this destination
		places, err := ts.tripPlaceRepository.GetByTripID(dest.TripDestinationID)
		if err != nil {
			return nil, err
		}

		for _, act := range places {
			destDTO.Places = append(destDTO.Places, dto.TripPlaceDTO{
				TripPlaceID:       act.TripPlaceID,
				TripDestinationID: act.TripDestinationID,
				PlaceID:           act.PlaceID,
				ScheduledDate:     act.ScheduledDate,
				StartTime:         act.StartTime,
				EndTime:           act.EndTime,
				Notes:             act.Notes,
			})
		}

		// Get restaurants for this destination
		restaurants, err := ts.tripRestaurantRepository.GetByTripID(dest.TripDestinationID)
		if err != nil {
			return nil, err
		}

		for _, rest := range restaurants {
			destDTO.Restaurants = append(destDTO.Restaurants, dto.TripRestaurantDTO{
				TripRestaurantID:  rest.TripRestaurantID,
				TripDestinationID: rest.TripDestinationID,
				RestaurantID:      rest.RestaurantID,
				MealDate:          rest.MealDate,
				StartTime:         rest.StartTime,
				EndTime:           rest.EndTime,
				ReservationInfo:   rest.ReservationInfo,
				Notes:             rest.Notes,
			})
		}

		tripDTO.TripDestinations = append(tripDTO.TripDestinations, destDTO)
	}

	return tripDTO, nil
}

func (ts *tripService) CallAISuggestTrip(activities dto.TripSuggestionRequest, endpoint string) (*dto.CreateTripRequestByDate, error) {
	client := &http.Client{
		Timeout: 100000 * time.Second,
	}

	var buf bytes.Buffer
	if err := json.NewEncoder(&buf).Encode(activities); err != nil {
		return nil, fmt.Errorf("failed to encode travel preference as json: %w", err)
	}

	aiURL := fmt.Sprintf("http://%s:%s%s",
		config.AppConfig.AI.Host,
		config.AppConfig.AI.Port,
		endpoint,
	)

	req, err := http.NewRequest("POST", aiURL, &buf)
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

	var rsp dto.CreateTripRequestByDate
	if err := json.NewDecoder(resp.Body).Decode(&rsp); err != nil {
		return nil, fmt.Errorf("failed to decode AI service response: %w", err)
	}
	return &rsp, nil
}

func (ts *tripService) SuggestTrip(activities dto.TripSuggestionRequest, endpoint string) (*dto.CreateTripRequestByDate, error) {
	// suggestionByDate, err := ts.CallAISuggestTrip(activities, endpoint)
	suggestionByDate, err := ts.CallAISuggestTrip(activities, endpoint)
	if err != nil {
		return nil, fmt.Errorf("failed to get trip suggestion: %w", err)
	}
	suggestion, err := dto.ConvertToCreateTripRequest(*suggestionByDate)
	if err != nil {
		return nil, fmt.Errorf("failed to convert trip suggestion: %w", err)
	}
	newSuggestionByDate, err := dto.ConvertToCreateTripRequestByDate(suggestion)
	if err != nil {
		return nil, fmt.Errorf("failed to convert trip suggestion by: %w", err)
	}

	return &newSuggestionByDate, nil
}
