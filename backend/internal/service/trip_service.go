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
	CreateTrip(trip *dto.TripDTO) (string, error)
	SaveTrip(trip *dto.TripDTO) error
	GetTrip(tripID string) (*dto.TripDTOByDate, error)
	SuggestTrip(userID string, activities dto.TripSuggestionRequest, endpoint string) (*dto.TripDTOByDate, error)
	GetTravelPreference(tripID string) (*model.TravelPreference, error)
	CreateTravelPreference(tripID string, tp *model.TravelPreference) (string, error)
	UpdateActivity(activityType string, activityID string, updatedData dto.Activity) error
	GetTripsByUserID(userID string) ([]dto.TripDTOByDate, error)
}

type tripService struct {
	tripRepository              repository.TripRepository
	tripDestinationRepository   repository.TripDestinationRepository
	tripAccommodationRepository repository.TripAccommodationRepository
	tripPlaceRepository         repository.TripPlaceRepository
	tripRestaurantRepository    repository.TripRestaurantRepository
	travelPreferenceRepository  repository.TravelPreferenceRepository
}

func NewTripService(
	tripRepo repository.TripRepository,
	tripDestinationRepo repository.TripDestinationRepository,
	accommodationRepo repository.TripAccommodationRepository,
	placeRepo repository.TripPlaceRepository,
	restaurantRepo repository.TripRestaurantRepository,
	tpRepo repository.TravelPreferenceRepository,
) TripService {
	return &tripService{
		tripRepository:              tripRepo,
		tripDestinationRepository:   tripDestinationRepo,
		tripAccommodationRepository: accommodationRepo,
		tripPlaceRepository:         placeRepo,
		tripRestaurantRepository:    restaurantRepo,
		travelPreferenceRepository:  tpRepo,
	}
}

func (ts *tripService) CreateTrip(trip *dto.TripDTO) (string, error) {
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

		// Fix for empty destination_id issue
		destinationID := destReq.DestinationID
		if destinationID == "" {
			// Set a default destination if none provided
			// Using "DEFAULT" as a placeholder - this should be a valid destination_id in your database
			destinationID = "DEFAULT"

			// Log the missing destination_id issue
			fmt.Printf("Warning: Empty destination_id found. Using default value: %s\n", destinationID)
		}

		tripDest := &model.TripDestination{
			TripDestinationID: destID,
			TripID:            tripID,
			DestinationID:     destinationID,
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
				PriceAIEstimate:     acc.PriceAIEstimate,
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
				PriceAIEstimate:   act.PriceAIEstimate,
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
				PriceAIEstimate:   rest.PriceAIEstimate,
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
				PriceAIEstimate:     acc.PriceAIEstimate,
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
				PriceAIEstimate:   act.PriceAIEstimate,
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
				PriceAIEstimate:   rest.PriceAIEstimate,
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

func (ts *tripService) GetTrip(tripID string) (*dto.TripDTOByDate, error) {
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

	// Update TripStatus based on today's date relative to StartDate and EndDate
	today := time.Now().Truncate(24 * time.Hour)
	if tripDTO.TripStatus != "cancelled" {
		if today.Equal(tripDTO.StartDate.AddDate(0, 0, -1)) {
			tripDTO.TripStatus = "upcomming"
		} else if today.Equal(tripDTO.StartDate) {
			tripDTO.TripStatus = "happening"
		} else if today.After(tripDTO.EndDate) {
			tripDTO.TripStatus = "completed"
		}
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
				PriceAIEstimate:     acc.PriceAIEstimate,
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
				PriceAIEstimate:   act.PriceAIEstimate,
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
				PriceAIEstimate:   rest.PriceAIEstimate,
			})
		}

		tripDTO.TripDestinations = append(tripDTO.TripDestinations, destDTO)
	}
	tripDTOByDate, err := dto.ConvertTripDTOByDate(*tripDTO)
	if err != nil {
		return nil, err
	}
	return &tripDTOByDate, nil
}

func (ts *tripService) CallAISuggestTrip(activities dto.TripSuggestionRequest, endpoint string) (*dto.TripDTOByDate, error) {
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
		Status string            `json:"status"`
		Plan   dto.TripDTOByDate `json:"plan"`
		Error  *string           `json:"error"`
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

func (ts *tripService) mockAISuggestTrip(activities dto.TripSuggestionRequest, endpoint string) (*dto.TripDTOByDate, error) {
	sampleJSON := `
{
    "trip_name": "Trip to Hanoi",
    "start_date": "2025-05-10",
    "end_date": "2025-05-12",
    "user_id": "user123",
    "destination_id": "hanoi",
    "plan_by_day": [
        {
            "date": "2025-05-10",
            "day_title": "Ngày 1: Khám phá nét cổ kính của Hà Nội",
            "segments": [
                {
                    "time_of_day": "morning",
                    "activities": [
                        {
                            "id": "hotel_008170",
                            "type": "accommodation",
                            "name": "Luxury Hanoi Hotel",
                            "start_time": "08:00",
                            "end_time": "11:00",
                            "description": "Thư giãn tại khách sạn sang trọng trong trung tâm thành phố.",
                            "location": "Hà Nội",
                            "rating": 4.5,
                            "price": 850000,
                            "image_url": "",
                            "url": "",
                            "price_ai_estimate": 3000000.0
                        }
                    ]
                },
                {
                    "time_of_day": "afternoon",
                    "activities": [
                        {
                            "id": "place_000003",
                            "type": "place",
                            "name": "Chuong Tailor",
                            "start_time": "13:00",
                            "end_time": "16:00",
                            "description": "Trải nghiệm làm đồ thủ công truyền thống tại Chuong Tailor.",
                            "address": "Hà Nội",
                            "categories": "shopping",
                            "rating": 4.2,
                            "price": 150000,
                            "image_url": "",
                            "url": "",
                            "price_ai_estimate": 300000.0
                        }
                    ]
                },
                {
                    "time_of_day": "evening",
                    "activities": [
                        {
                            "id": "restaurant_001958",
                            "type": "restaurant",
                            "name": "Vietnamese Family Meal",
                            "start_time": "18:00",
                            "end_time": "20:00",
                            "description": "Thưởng thức bữa tối ấm cúng với món ăn gia đình Việt Nam.",
                            "address": "Hà Nội",
                            "cuisines": "Vietnamese",
                            "rating": 4.6,
                            "phone": "",
                            "image_url": "",
                            "url": "",
                            "price_ai_estimate": 350000.0
                        }
                    ]
                }
            ],
            "daily_tips": [
                "Nên bắt đầu sớm từ 6-8h sáng để tránh nóng và đông đúc.",
                "Mang theo nước và đồ ăn nhẹ để giữ năng lượng.",
                "Sử dụng bản đồ offline để không phụ thuộc vào internet.",
                "Mặc quần áo thoải mái và mang giày đi bộ.",
                "Đổi tiền trước khi đi để tránh rắc rối.",
                "Hãy cẩn thận với tài sản cá nhân khi đi qua khu vực đông người.",
                "Tham quan Văn Miếu Quốc Tử Giám vào buổi sáng để tránh đông đúc.",
                "Thưởng thức phở tại một quán nổi tiếng gần Hồ Hoàn Kiếm.",
                "Chụp ảnh tại Nhà Thờ Lớn Hà Nội vào buổi chiều để có ánh sáng đẹp."
            ]
        },
        {
            "date": "2025-05-11",
            "day_title": "Ngày 2: Thưởng thức Hà Nội qua ẩm thực",
            "segments": [
                {
                    "time_of_day": "morning",
                    "activities": [
                        {
                            "id": "restaurant_000098",
                            "type": "restaurant",
                            "name": "Family Restaurant",
                            "start_time": "08:00",
                            "end_time": "10:00",
                            "description": "Bạn sẽ được thưởng thức bữa sáng với các món ăn truyền thống của Hà Nội.",
                            "price_ai_estimate": 120000.0
                        }
                    ]
                },
                {
                    "time_of_day": "afternoon",
                    "activities": [
                        {
                            "id": "restaurant_000623",
                            "type": "restaurant",
                            "name": "Little Hanoi Restaurants",
                            "start_time": "12:00",
                            "end_time": "14:00",
                            "description": "Hãy tận hưởng bữa trưa với những món ăn đặc trưng của Hà Nội.",
                            "price_ai_estimate": 150000.0
                        }
                    ]
                },
                {
                    "time_of_day": "evening",
                    "activities": [
                        {
                            "id": "restaurant_000494",
                            "type": "restaurant",
                            "name": "Maison Sen",
                            "start_time": "18:00",
                            "end_time": "20:00",
                            "description": "Kết thúc ngày với bữa tối tại một trong những nhà hàng nổi tiếng nhất Hà Nội.",
                            "price_ai_estimate": 500000.0
                        }
                    ]
                }
            ],
            "daily_tips": [
                "Đặt chỗ trước và đến Maison Sen vào buổi tối để có trải nghiệm tốt nhất.",
                "Di chuyển giữa các nhà hàng bằng taxi hoặc xe ôm công nghệ để tiết kiệm thời gian.",
                "Dự kiến chi phí mỗi bữa ăn từ 200,000 - 500,000 VND tùy món.",
                "Tránh đến Maison Sen vào giờ cao điểm 18h-20h nếu không đặt chỗ trước.",
                "Tìm hiểu khuyến mãi hoặc combo tại Family Restaurant để tiết kiệm chi phí.",
                "Giữ thái độ lịch sự khi giao tiếp với nhân viên nhà hàng và hỏi về cách ăn đúng cách."
            ]
        },
        {
            "date": "2025-05-12",
            "day_title": "Ngày 3: Trải nghiệm văn hóa ẩm thực Hà Nội",
            "segments": [
                {
                    "time_of_day": "morning",
                    "activities": [
                        {
                            "id": "restaurant_000231",
                            "type": "restaurant",
                            "name": "Minh´s Family Cooking",
                            "start_time": "08:30",
                            "end_time": "10:30",
                            "description": "Học nấu ăn Việt Nam trong bầu không khí gia đình tại Minh's Family Cooking.",
                            "address": "Hà Nội",
                            "cuisines": "Việt Nam",
                            "rating": 4.3,
                            "phone": "+84981234567",
                            "image_url": "",
                            "url": "",
                            "price_ai_estimate": 500000.0
                        }
                    ]
                },
                {
                    "time_of_day": "afternoon",
                    "activities": [
                        {
                            "id": "restaurant_001808",
                            "type": "restaurant",
                            "name": "Freedom Hostel Restaurant",
                            "start_time": "12:00",
                            "end_time": "14:00",
                            "description": "Thưởng thức bữa trưa tại Freedom Hostel Restaurant, nơi có món ăn đặc trưng của Hà Nội.",
                            "address": "Hà Nội",
                            "cuisines": "Việt Nam",
                            "rating": 4.1,
                            "phone": "+84981234568",
                            "image_url": "",
                            "url": "",
                            "price_ai_estimate": 150000.0
                        },
                        {
                            "id": "restaurant_000498",
                            "type": "restaurant",
                            "name": "Vi Hanoi Restaurant & Cafe",
                            "start_time": "14:30",
                            "end_time": "16:00",
                            "description": "Thưởng thức cà phê Việt Nam tại Vi Hanoi Restaurant & Cafe.",
                            "address": "Hà Nội",
                            "cuisines": "Cafe",
                            "rating": 4.2,
                            "phone": "+84981234569",
                            "image_url": "",
                            "url": "",
                            "price_ai_estimate": 200000.0
                        }
                    ]
                },
                {
                    "time_of_day": "evening",
                    "activities": [
                        {
                            "id": "restaurant_000658",
                            "type": "restaurant",
                            "name": "Bamboo Bar",
                            "start_time": "18:00",
                            "end_time": "20:00",
                            "description": "Cuối ngày, thư giãn tại Bamboo Bar với cocktail tuyệt vời.",
                            "address": "Hà Nội",
                            "cuisines": "Bar",
                            "rating": 4.5,
                            "phone": "+84981234570",
                            "image_url": "",
                            "url": "",
                            "price_ai_estimate": 300000.0
                        }
                    ]
                }
            ],
            "daily_tips": [
                "Bắt đầu ngày mới với lớp học nấu ăn tại Minh's Family Cooking từ 08:30 - 10:30.",
                "Sử dụng xe ôm công nghệ hoặc taxi để di chuyển giữa các địa điểm trong ngày.",
                "Dự kiến chi phí cả ngày khoảng 700,000 - 900,000 VND, chuẩn bị thêm tiền mặt để tiện thanh toán.",
                "Tránh ăn quá no tại một địa điểm để thưởng thức nhiều món khác nhau trong ngày.",
                "Hỏi trước về nguyên liệu nếu có dị ứng thực phẩm.",
                "Hỏi về món ăn đặc biệt trong ngày hoặc thực đơn combo để tiết kiệm chi phí.",
                "Tìm hiểu giờ khuyến mãi \"happy hour\" tại Bamboo Bar.",
                "Tôn trọng phong tục tập quán địa phương khi tham gia lớp học nấu ăn.",
                "Thử cà phê trứng tại Vi Hanoi Cafe và các món đặc trưng như phở, bún chả tại Freedom Hostel Restaurant.",
                "Tôn trọng không gian chung và giữ thái độ lịch sự tại Bamboo Bar."
            ]
        }
    ]
}

	`
	var result dto.TripDTOByDate
	if err := json.Unmarshal([]byte(sampleJSON), &result); err != nil {
		return nil, fmt.Errorf("failed to unmarshal mock JSON: %w", err)
	}
	return &result, nil
}

func (ts *tripService) SuggestTrip(userID string, activities dto.TripSuggestionRequest, endpoint string) (*dto.TripDTOByDate, error) {
	// suggestionByDate, err := ts.CallAISuggestTrip(activities, endpoint)
	suggestionByDate, err := ts.mockAISuggestTrip(activities, endpoint)
	if err != nil {
		return nil, fmt.Errorf("failed to get trip suggestion: %w", err)
	}
	suggestion, err := dto.ConvertTripDTO(*suggestionByDate)
	if err != nil {
		return nil, fmt.Errorf("failed to convert trip suggestion: %w", err)
	}
	suggestion.UserID = userID

	tripID, err := ts.CreateTrip(&suggestion)
	if err != nil {
		return nil, fmt.Errorf("failed to create trip: %w", err)
	}

	newSuggestionByDate, err := dto.ConvertTripDTOByDate(suggestion)
	if err != nil {
		return nil, fmt.Errorf("failed to convert trip suggestion: %w", err)
	}
	suggestionByDate.TripID = tripID
	newSuggestionByDate.TripID = tripID
	fmt.Println("Converted suggestion: ", newSuggestionByDate)
	return suggestionByDate, nil
}

func (ts *tripService) GetTravelPreference(tripID string) (*model.TravelPreference, error) {
	tp, err := ts.travelPreferenceRepository.GetByTripID(tripID)
	if err != nil {
		return nil, err
	}
	return &tp, nil
}

func (ts *tripService) CreateTravelPreference(tripID string, tp *model.TravelPreference) (string, error) {
	// Generate UUID for travel preference
	tp.TravelPreferenceID = uuid.New().String()
	tp.TripID = tripID

	// Begin transaction
	tx := ts.travelPreferenceRepository.(*repository.GormTravelPreferenceRepository).DB.Begin()

	// Create travel preference
	if err := tx.Create(tp).Error; err != nil {
		tx.Rollback()
		return "", err
	}

	// Commit transaction
	if err := tx.Commit().Error; err != nil {
		tx.Rollback()
		return "", err
	}

	return tp.TravelPreferenceID, nil
}

func (ts *tripService) UpdateActivity(activityType string, activityID string, updatedData dto.Activity) error {
	switch activityType {
	case "accommodation":
		// Update accommodation
		newTripAccommodation, err := ts.tripAccommodationRepository.GetByID(activityID)
		if err != nil {
			return fmt.Errorf("failed to get accommodation: %w", err)
		}
		newTripAccommodation.Notes = updatedData.Description
		newTripAccommodation.PriceAIEstimate = updatedData.PriceAIEstimate
		newTripAccommodation.AccommodationID = updatedData.ID

		if err := ts.tripAccommodationRepository.Update(&newTripAccommodation); err != nil {
			return fmt.Errorf("failed to update accommodation: %w", err)
		}
	case "restaurant":
		// Update restaurant
		newTripRestaurant, err := ts.tripRestaurantRepository.GetByID(activityID)
		if err != nil {
			return fmt.Errorf("failed to get restaurant: %w", err)
		}
		newTripRestaurant.Notes = updatedData.Description
		newTripRestaurant.PriceAIEstimate = updatedData.PriceAIEstimate
		newTripRestaurant.RestaurantID = updatedData.ID

		if err := ts.tripRestaurantRepository.Update(&newTripRestaurant); err != nil {
			return fmt.Errorf("failed to update restaurant: %w", err)
		}
	case "place":
		// Update place
		newTripPlace, err := ts.tripPlaceRepository.GetByID(activityID)
		if err != nil {
			return fmt.Errorf("failed to get place: %w", err)
		}
		newTripPlace.Notes = updatedData.Description
		newTripPlace.PriceAIEstimate = updatedData.PriceAIEstimate
		newTripPlace.PlaceID = updatedData.ID

		if err := ts.tripPlaceRepository.Update(&newTripPlace); err != nil {
			return fmt.Errorf("failed to update place: %w", err)
		}
	default:
		return fmt.Errorf("invalid activity type: %s", activityType)
	}
	return nil
}

func (ts *tripService) GetTripsByUserID(userID string) ([]dto.TripDTOByDate, error) {
	// Retrieve trips by user ID
	trips, err := ts.tripRepository.GetByUserIDWithAssociation(userID)
	if err != nil {
		return nil, fmt.Errorf("failed to retrieve trips for user ID %s: %w", userID, err)
	}

	// Convert trips to DTOs
	var tripDTOs []dto.TripDTO
	for _, trip := range trips {
		tripDTO := dto.TripDTO{
			TripID:     trip.TripID,
			UserID:     trip.UserID,
			TripName:   trip.TripName,
			StartDate:  trip.StartDate,
			EndDate:    trip.EndDate,
			Budget:     trip.Budget,
			TripStatus: trip.TripStatus,
		}

		// Add TripDestinations
		for _, dest := range trip.TripDestinations {
			destDTO := dto.TripDestinationDTO{
				TripDestinationID: dest.TripDestinationID,
				TripID:            dest.TripID,
				DestinationID:     dest.DestinationID,
				ArrivalDate:       dest.ArrivalDate,
				DepartureDate:     dest.DepartureDate,
				OrderNum:          dest.OrderNum,
			}

			// Add TripAccommodations
			for _, acc := range dest.Accommodations {
				destDTO.Accommodations = append(destDTO.Accommodations, dto.TripAccommodationDTO{
					TripAccommodationID: acc.TripAccommodationID,
					TripDestinationID:   acc.TripDestinationID,
					AccommodationID:     acc.AccommodationID,
					CheckInDate:         acc.CheckInDate,
					CheckOutDate:        acc.CheckOutDate,
					StartTime:           acc.StartTime,
					EndTime:             acc.EndTime,
					PriceAIEstimate:     acc.PriceAIEstimate,
					Notes:               acc.Notes,
				})
			}

			// Add TripPlaces
			for _, place := range dest.Places {
				destDTO.Places = append(destDTO.Places, dto.TripPlaceDTO{
					TripPlaceID:       place.TripPlaceID,
					TripDestinationID: place.TripDestinationID,
					PlaceID:           place.PlaceID,
					ScheduledDate:     place.ScheduledDate,
					StartTime:         place.StartTime,
					EndTime:           place.EndTime,
					Notes:             place.Notes,
					PriceAIEstimate:   place.PriceAIEstimate,
				})
			}

			// Add TripRestaurants
			for _, rest := range dest.Restaurants {
				destDTO.Restaurants = append(destDTO.Restaurants, dto.TripRestaurantDTO{
					TripRestaurantID:  rest.TripRestaurantID,
					TripDestinationID: rest.TripDestinationID,
					RestaurantID:      rest.RestaurantID,
					MealDate:          rest.MealDate,
					StartTime:         rest.StartTime,
					EndTime:           rest.EndTime,
					ReservationInfo:   rest.ReservationInfo,
					Notes:             rest.Notes,
					PriceAIEstimate:   rest.PriceAIEstimate,
				})
			}

			tripDTO.TripDestinations = append(tripDTO.TripDestinations, destDTO)
		}

		tripDTOs = append(tripDTOs, tripDTO)
	}

	// Convert TripDTOs to TripDTOByDate
	var tripDTOsByDate []dto.TripDTOByDate
	for _, trip := range tripDTOs {
		tripDTOByDate, err := dto.ConvertTripDTOByDate(trip)
		if err != nil {
			return nil, fmt.Errorf("failed to convert trip to DTO: %w", err)
		}
		tripDTOsByDate = append(tripDTOsByDate, tripDTOByDate)
	}

	return tripDTOsByDate, nil
}
