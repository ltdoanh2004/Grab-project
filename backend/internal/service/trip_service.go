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

	"github.com/google/uuid"
)

type TripService interface {
	CreateTrip(trip *dto.CreateTripRequest) (string, error)
	SaveTrip(trip *dto.TripDTO) error
	GetTrip(tripID string) (*dto.TripDTO, error)
	SuggestTrip(userID string, activities dto.TripSuggestionRequest, endpoint string) (*dto.CreateTripRequestByDate, error)
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
				StartTime:           acc.StartTime,
				EndTime:             acc.EndTime,
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
				StartTime:           acc.StartTime,
				EndTime:             acc.EndTime,
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
				StartTime:           acc.StartTime,
				EndTime:             acc.EndTime,
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

	// Prepare the data for AI service - we need to convert image arrays to proper format
	// First, handle accommodations
	for i, acc := range activities.Accommodation.Accommodations {
		// If the accommodation has images, extract the first image URL
		if len(acc.Images) > 0 {
			// Add an image_url field with the URL from the first image
			activities.Accommodation.Accommodations[i].Link = acc.Images[0].URL

			// For debugging
			fmt.Printf("Setting accommodation image URL for %s: %s\n", acc.Name, acc.Images[0].URL)
		}
	}

	// Handle places
	for i, place := range activities.Places.Places {
		// If the place has images, extract the first image URL
		if len(place.Images) > 0 {
			// Set the main image field to the URL from the first image
			activities.Places.Places[i].MainImage = place.Images[0].URL

			// For debugging
			fmt.Printf("Setting place image URL for %s: %s\n", place.Name, place.Images[0].URL)
		}
	}

	// Handle restaurants - just ensure photo_url is set properly
	// (restaurants already use a direct photo_url field)

	// Dump the full request content for debugging
	requestJSON, _ := json.MarshalIndent(activities, "", "  ")
	fmt.Println("==== SENDING REQUEST TO AI ====")
	fmt.Println(string(requestJSON))
	fmt.Println("===============================")

	var buf bytes.Buffer
	if err := json.NewEncoder(&buf).Encode(activities); err != nil {
		return nil, fmt.Errorf("failed to encode travel preference as json: %w", err)
	}

	aiURL := fmt.Sprintf("http://%s:%s%s",
		config.AppConfig.AI.Host,
		config.AppConfig.AI.Port,
		endpoint,
	)

	fmt.Println("Sending request to:", aiURL)

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

	fmt.Printf("AI Response Status: %s (%d)\n", resp.Status, resp.StatusCode)

	if resp.StatusCode != http.StatusOK {
		// Try to read error response body
		errBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("AI service returned non-200 status code: %d, Body: %s", resp.StatusCode, string(errBody))
	}

	// Read the entire response for debugging
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	fmt.Println("==== AI RESPONSE ====")
	fmt.Println(string(responseBody))
	fmt.Println("=====================")

	// Parse the API response which has structure: {"status": "success", "plan": {...}, "error": null}
	var apiResponse struct {
		Status string                      `json:"status"`
		Plan   dto.CreateTripRequestByDate `json:"plan"`
		Error  *string                     `json:"error"`
	}

	if err := json.Unmarshal(responseBody, &apiResponse); err != nil {
		return nil, fmt.Errorf("failed to decode AI service response: %w", err)
	}

	// Check if there's an error in the API response
	if apiResponse.Error != nil && *apiResponse.Error != "" {
		return nil, fmt.Errorf("AI service returned error: %s", *apiResponse.Error)
	}

	// Check if status is not success
	if apiResponse.Status != "success" {
		return nil, fmt.Errorf("AI service returned non-success status: %s", apiResponse.Status)
	}

	// Check if plan data is valid
	if apiResponse.Plan.TripName == "" {
		return nil, fmt.Errorf("AI service returned empty plan data")
	}

	fmt.Printf("Successfully parsed plan: %s, %d days, from %s to %s\n",
		apiResponse.Plan.TripName,
		len(apiResponse.Plan.PlanByDay),
		apiResponse.Plan.StartDate,
		apiResponse.Plan.EndDate)

	return &apiResponse.Plan, nil
}

func (ts *tripService) mockAISuggestTrip(activities dto.TripSuggestionRequest, endpoint string) (*dto.CreateTripRequestByDate, error) {
	sampleJSON := `
{
    "trip_name": "Trip to Hanoi",
    "start_date": "2025-05-06",
    "end_date": "2025-05-08",
    "user_id": "user123",
    "destination": "hanoi",
    "plan_by_day": [
        {
            "date": "2025-05-06",
            "day_title": "Ngày 1: Khám phá nét đẹp thủ đô Hà Nội",
            "segments": [
                {
                    "time_of_day": "morning",
                    "activities": [
                        {
                            "id": "hotel_006100",
                            "type": "accommodation",
                            "name": "Hanoi Capital Hostel & Travel",
                            "start_time": "08:00",
                            "end_time": "10:00",
                            "description": "Bạn sẽ được tận hưởng bữa sáng ngon miệng tại khách sạn."
                        },
                        {
                            "id": "place_000481",
                            "type": "place",
                            "name": "Ha Noi",
                            "start_time": "10:30",
                            "end_time": "12:00",
                            "description": "Chúng ta sẽ khám phá nét đẹp của thủ đô Hà Nội."
                        }
                    ]
                },
                {
                    "time_of_day": "afternoon",
                    "activities": [
                        {
                            "id": "restaurant_020781",
                            "type": "restaurant",
                            "name": "Beefsteak Nam Sơn - Nguyễn Thị Minh Khai",
                            "start_time": "12:30",
                            "end_time": "13:30",
                            "description": "Bạn sẽ được thưởng thức bữa trưa tại Beefsteak Nam Sơn."
                        },
                        {
                            "id": "place_011825",
                            "type": "place",
                            "name": "Hanoi Old Quarter",
                            "start_time": "14:00",
                            "end_time": "16:30",
                            "description": "Chúng ta sẽ tham quan phố cổ Hà Nội, nơi lưu giữ nét cổ kính của thủ đô."
                        }
                    ]
                },
                {
                    "time_of_day": "evening",
                    "activities": [
                        {
                            "id": "restaurant_000880",
                            "type": "restaurant",
                            "name": "Phở Hà Nội - Hồng Hà",
                            "start_time": "18:00",
                            "end_time": "19:00",
                            "description": "Thưởng thức món phở truyền thống, đặc sản của Hà Nội."
                        },
                        {
                            "id": "place_000159",
                            "type": "place",
                            "name": "City Game Hanoi",
                            "start_time": "19:30",
                            "end_time": "21:30",
                            "description": "Chúng ta sẽ kết thúc ngày bằng những trò chơi vui nhộn tại City Game Hanoi."
                        }
                    ]
                }
            ]
        },
        {
            "date": "2025-05-07",
            "day_title": "Ngày 2: Hành trình khám phá Hà Nội cổ kính",
            "segments": [
                {
                    "time_of_day": "morning",
                    "activities": [
                        {
                            "id": "hotel_006100",
                            "type": "accommodation",
                            "name": "Hanoi Capital Hostel & Travel",
                            "start_time": "08:00",
                            "end_time": "10:00",
                            "description": "Bạn sẽ bắt đầu ngày mới với không gian thoáng đãng, yên tĩnh tại khách sạn.",
                            "location": "Hà Nội",
                            "rating": 4.5,
                            "price": 850000,
                            "image_url": "",
                            "url": ""
                        },
                        {
                            "id": "place_000481",
                            "type": "place",
                            "name": "Ha Noi (Hanoi, Vietnam)",
                            "start_time": "10:30",
                            "end_time": "12:00",
                            "description": "Khám phá nét đẹp truyền thống, văn hóa phong phú của Hà Nội.",
                            "address": "Hà Nội",
                            "categories": "sightseeing",
                            "rating": 4.0,
                            "price": 50000,
                            "image_url": "",
                            "url": ""
                        }
                    ]
                },
                {
                    "time_of_day": "afternoon",
                    "activities": [
                        {
                            "id": "restaurant_020781",
                            "type": "restaurant",
                            "name": "Beefsteak Nam Sơn - Nguyễn Thị Minh Khai",
                            "start_time": "12:30",
                            "end_time": "13:30",
                            "description": "Thưởng thức bữa trưa với thịt bò nướng thơm ngon, mềm mại.",
                            "address": "Hà Nội",
                            "cuisines": "Steakhouse",
                            "rating": 4.5,
                            "phone": "",
                            "image_url": "",
                            "url": ""
                        },
                        {
                            "id": "place_011825",
                            "type": "place",
                            "name": "Hanoi Old Quarter",
                            "start_time": "14:00",
                            "end_time": "17:00",
                            "description": "Dạo quanh phố cổ Hà Nội, thưởng thức không khí sôi động, đậm chất lịch sử.",
                            "address": "Hà Nội",
                            "categories": "sightseeing",
                            "rating": 4.5,
                            "price": 0,
                            "image_url": "",
                            "url": ""
                        }
                    ]
                },
                {
                    "time_of_day": "evening",
                    "activities": [
                        {
                            "id": "restaurant_000880",
                            "type": "restaurant",
                            "name": "Phở Hà Nội - Hồng Hà",
                            "start_time": "18:00",
                            "end_time": "19:00",
                            "description": "Thưởng thức hương vị đặc trưng của phở Hà Nội, món ăn truyền thống.",
                            "address": "Hà Nội",
                            "cuisines": "Vietnamese",
                            "rating": 4.2,
                            "phone": "",
                            "image_url": "",
                            "url": ""
                        },
                        {
                            "id": "place_000300",
                            "type": "place",
                            "name": "Ha Noi Nail",
                            "start_time": "19:30",
                            "end_time": "21:00",
                            "description": "Chăm sóc bản thân tại Ha Noi Nail, tận hưởng dịch vụ chất lượng cao.",
                            "address": "Hà Nội",
                            "categories": "beauty_salon",
                            "rating": 4.0,
                            "price": 150000,
                            "image_url": "",
                            "url": ""
                        }
                    ]
                }
            ]
        },
        {
            "date": "2025-05-08",
            "day_title": "Ngày 3: Khám phá văn hóa và ẩm thực Hà Nội",
            "segments": [
                {
                    "time_of_day": "morning",
                    "activities": [
                        {
                            "id": "hotel_001980",
                            "type": "accommodation",
                            "name": "GRAND CITITEL Hanoi Hotel & Spa",
                            "start_time": "08:00",
                            "end_time": "10:00",
                            "description": "Bạn sẽ được thưởng thức bữa sáng ngon miệng tại khách sạn."
                        },
                        {
                            "id": "place_011825",
                            "type": "place",
                            "name": "Hanoi Old Quarter",
                            "start_time": "10:30",
                            "end_time": "12:00",
                            "description": "Chúng ta sẽ dạo quanh phố cổ Hà Nội, nơi lịch sử và hiện đại giao thoa."
                        }
                    ]
                },
                {
                    "time_of_day": "afternoon",
                    "activities": [
                        {
                            "id": "restaurant_020781",
                            "type": "restaurant",
                            "name": "Beefsteak Nam Sơn - Nguyễn Thị Minh Khai",
                            "start_time": "12:30",
                            "end_time": "14:00",
                            "description": "Bạn sẽ được thưởng thức bữa trưa với món bò nổi tiếng của Hà Nội."
                        },
                        {
                            "id": "place_011374",
                            "type": "place",
                            "name": "Hanoi Old Quarter",
                            "start_time": "14:30",
                            "end_time": "17:00",
                            "description": "Tiếp tục hành trình khám phá phố cổ, thăm các cửa hàng lưu niệm và nghệ thuật đường phố."
                        }
                    ]
                },
                {
                    "time_of_day": "evening",
                    "activities": [
                        {
                            "id": "restaurant_000880",
                            "type": "restaurant",
                            "name": "Phở Hà Nội - Hồng Hà",
                            "start_time": "18:00",
                            "end_time": "20:00",
                            "description": "Bạn sẽ được thưởng thức món phở nổi tiếng thế giới trong bữa tối."
                        },
                        {
                            "id": "place_000159",
                            "type": "place",
                            "name": "City Game Hanoi",
                            "start_time": "20:30",
                            "end_time": "22:00",
                            "description": "Chúng ta sẽ kết thúc ngày bằng một đêm vui chơi tại City Game Hanoi."
                        }
                    ]
                }
            ]
        }
    ]
}
`
	var result dto.CreateTripRequestByDate
	if err := json.Unmarshal([]byte(sampleJSON), &result); err != nil {
		return nil, fmt.Errorf("failed to unmarshal mock JSON: %w", err)
	}
	return &result, nil
}

func (ts *tripService) SuggestTrip(userID string, activities dto.TripSuggestionRequest, endpoint string) (*dto.CreateTripRequestByDate, error) {
	suggestionByDate, err := ts.CallAISuggestTrip(activities, endpoint)
	// suggestionByDate, err := ts.mockAISuggestTrip(activities, endpoint)
	if err != nil {
		return nil, fmt.Errorf("failed to get trip suggestion: %w", err)
	}
	suggestion, err := dto.ConvertToCreateTripRequest(*suggestionByDate)
	if err != nil {
		return nil, fmt.Errorf("failed to convert trip suggestion: %w", err)
	}
	suggestion.UserID = userID

	_, err = ts.CreateTrip(&suggestion)
	if err != nil {
		return nil, fmt.Errorf("failed to create trip: %w", err)
	}

	newSuggestionByDate, err := dto.ConvertToCreateTripRequestByDate(suggestion)
	if err != nil {
		return nil, fmt.Errorf("failed to convert trip suggestion: %w", err)
	}
	fmt.Println("Converted suggestion: ", newSuggestionByDate)

	return suggestionByDate, nil
}
