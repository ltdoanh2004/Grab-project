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
  "start_date": "2025-05-04",
  "end_date": "2025-05-06",
  "user_id": "user123",
  "destination": "hanoi",
  "plan_by_day": [
	{
	  "date": "2025-05-04",
	  "day_title": "Ngày 1: Khám phá biển",
	  "segments": [
		{
		  "time_of_day": "morning",
		  "activities": [
			{
			  "id": "place_morning_day1",
			  "type": "place",
			  "name": "WanderOn",
			  "start_time": "08:00",
			  "end_time": "10:00",
			  "description": "WanderOn là một công ty du lịch tuyệt vời tại Hà Nội. Công ty cung cấp các tour du lịch chuyên biệt tại Hà Nội và các tỉnh lân cận, với những trải nghiệm thú vị và đội ngũ hướng dẫn viên chuyên nghiệp. Nếu bạn muốn khám phá Hà Nội theo cách đặc biệt và đầy thú vị, hãy đến với WanderOn. Địa",
			  "address": "",
			  "categories": "sightseeing",
			  "duration": "2h",
			  "opening_hours": "08:00-17:00",
			  "rating": 4.0,
			  "price": 0,
			  "image_url": "",
			  "url": ""
			}
		  ]
		},
		{
		  "time_of_day": "afternoon",
		  "activities": [
			{
			  "id": "place_011198",
			  "type": "place",
			  "name": "WanderOn",
			  "start_time": "14:00",
			  "end_time": "16:00",
			  "description": "An evolving & expanding backpacking travel community, we organize well-crafted tours for thousands of enthusiastic travelers. As professionals, travel is our passion & life-work; we have the knowledge & experience to ensure you enjoy an exceptional travel experience! It’s about going on a Trip ourselves. Talk to us about your Travel plans,& let our specialists make your dream holiday perfect!",
			  "address": "",
			  "categories": "",
			  "duration": "",
			  "opening_hours": "12:00 AM - 11:59 PM",
			  "rating": 4.9,
			  "price": 37.0,
			  "image_url": "",
			  "url": "https://www.tripadvisor.com/Attraction_Review-g304551-d15013133-Reviews-WanderOn-New_Delhi_National_Capital_Territory_of_Delhi.html"
			}
		  ]
		},
		{
		  "time_of_day": "evening",
		  "activities": [
			{
			  "id": "restaurant_022913",
			  "type": "restaurant",
			  "name": "Busan Korean Food - Nguyễn Tri Phương",
			  "start_time": "19:00",
			  "end_time": "21:00",
			  "description": "",
			  "address": "272A Nguyễn Tri Phương, P. 4, Quận 10, TP. HCM",
			  "cuisines": "",
			  "price_range": "",
			  "rating": 5.8,
			  "phone": "Đang cập nhật",
			  "services": [
				{
				  "name": "ShopeeFood",
				  "url": "https://www.deliverynow.vn/ho-chi-minh/busan-korean-food-nguyen-tri-phuong",
				  "type": 0
				}
			  ],
			  "image_url": "",
			  "url": "https://www.foody.vn/ho-chi-minh/busan-korean-food-nguyen-tri-phuong"
			}
		  ]
		}
	  ]
	},
	{
	  "date": "2025-05-05",
	  "day_title": "Ngày 2: Khám phá núi",
	  "segments": [
		{
		  "time_of_day": "morning",
		  "activities": [
			{
			  "id": "WanderOn_morning_day2",
			  "type": "place",
			  "name": "WanderOn",
			  "start_time": "08:00",
			  "end_time": "10:00",
			  "description": "WanderOn là một trong những địa điểm tuyệt vời để bắt đầu ngày mới. Nơi đây có khung cảnh đẹp và yên bình, mang lại cho bạn cảm giác thư thái khi ngắm nhìn một bức tranh thiên nhiên tuyệt vời của Hà Nội.",
			  "address": "Số 7 Ngõ 118 Đường Quán Thánh, Ba Đình, Hà Nội",
			  "categories": "sightseeing",
			  "duration": "",
			  "opening_hours": "08:00-17:00",
			  "rating": 4.0,
			  "price": 0,
			  "image_url": "",
			  "url": ""
			}
		  ]
		},
		{
		  "time_of_day": "afternoon",
		  "activities": [
			{
			  "id": "place_011608",
			  "type": "place",
			  "name": "WanderOn",
			  "start_time": "14:00",
			  "end_time": "16:00",
			  "description": "An evolving & expanding backpacking travel community, we organize well-crafted tours for thousands of enthusiastic travelers. As professionals, travel is our passion & life-work; we have the knowledge & experience to ensure you enjoy an exceptional travel experience! It’s about going on a Trip ourselves. Talk to us about your Travel plans,& let our specialists make your dream holiday perfect!",
			  "address": "",
			  "categories": "",
			  "duration": "",
			  "opening_hours": "12:00 AM - 11:59 PM",
			  "rating": 4.9,
			  "price": 37.0,
			  "image_url": "",
			  "url": "https://www.tripadvisor.com/Attraction_Review-g304551-d15013133-Reviews-WanderOn-New_Delhi_National_Capital_Territory_of_Delhi.html"
			}
		  ]
		},
		{
		  "time_of_day": "evening",
		  "activities": [
			{
			  "id": "restaurant_022911",
			  "type": "restaurant",
			  "name": "Trung Nguyên Legend Coffee - 219 Lý Tự Trọng",
			  "start_time": "19:00",
			  "end_time": "21:00",
			  "description": "",
			  "address": "219 Lý Tự Trọng, P. Bến Thành, Quận 1, TP. HCM",
			  "cuisines": "",
			  "price_range": "",
			  "rating": 7.66,
			  "phone": "(028) 38 258 847",
			  "services": [
				{
				  "name": "ShopeeFood",
				  "url": "https://www.deliverynow.vn/ho-chi-minh/trung-nguyen-legend-coffee-219-ly-tu-trong",
				  "type": 0
				}
			  ],
			  "image_url": "",
			  "url": "https://www.foody.vn/ho-chi-minh/trung-nguyen-legend-coffee-219-ly-tu-trong"
			}
		  ]
		}
	  ]
	},
	{
	  "date": "2025-05-06",
	  "day_title": "Ngày 3: Khám phá văn hóa",
	  "segments": [
		{
		  "time_of_day": "morning",
		  "activities": [
			{
			  "id": "place_morning_day3",
			  "type": "place",
			  "name": "WanderOn",
			  "start_time": "08:00",
			  "end_time": "10:00",
			  "description": "WanderOn là một trung tâm nghệ thuật và văn hóa của Hà Nội, nơi bạn có thể tìm hiểu về lịch sử, nghệ thuật và văn hóa dân tộc Việt Nam. Đón xem những buổi diễn trình diễn truyền thống đặc sắc và tham quan các triển lãm nghệ thuật độc đáo tại đây.",
			  "address": "Nguyễn Thị Minh Khai, Đống",
			  "categories": "sightseeing",
			  "duration": "2h",
			  "opening_hours": "08:00-17:00",
			  "rating": 4.0,
			  "price": 0,
			  "image_url": "",
			  "url": ""
			}
		  ]
		},
		{
		  "time_of_day": "afternoon",
		  "activities": [
			{
			  "id": "place_011475",
			  "type": "place",
			  "name": "WanderOn",
			  "start_time": "14:00",
			  "end_time": "16:00",
			  "description": "An evolving & expanding backpacking travel community, we organize well-crafted tours for thousands of enthusiastic travelers. As professionals, travel is our passion & life-work; we have the knowledge & experience to ensure you enjoy an exceptional travel experience! It’s about going on a Trip ourselves. Talk to us about your Travel plans,& let our specialists make your dream holiday perfect!",
			  "address": "",
			  "categories": "",
			  "duration": "",
			  "opening_hours": "12:00 AM - 11:59 PM",
			  "rating": 4.9,
			  "price": 37.0,
			  "image_url": "",
			  "url": "https://www.tripadvisor.com/Attraction_Review-g304551-d15013133-Reviews-WanderOn-New_Delhi_National_Capital_Territory_of_Delhi.html"
			}
		  ]
		},
		{
		  "time_of_day": "evening",
		  "activities": [
			{
			  "id": "restaurant_021947",
			  "type": "restaurant",
			  "name": "Cafe Zoom ",
			  "start_time": "19:00",
			  "end_time": "21:00",
			  "description": "",
			  "address": "169A Đề Thám, P. Phạm Ngũ Lão, Quận 1, TP. HCM",
			  "cuisines": "",
			  "price_range": "",
			  "rating": 7.55,
			  "phone": "(028) 39 203 897",
			  "services": [
				{
				  "name": "ShopeeFood",
				  "url": "https://www.deliverynow.vn/ho-chi-minh/cafe-zoom",
				  "type": 0
				}
			  ],
			  "image_url": "",
			  "url": "https://www.foody.vn/ho-chi-minh/cafe-zoom"
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

func (ts *tripService) SuggestTrip(activities dto.TripSuggestionRequest, endpoint string) (*dto.CreateTripRequestByDate, error) {
	suggestionByDate, err := ts.CallAISuggestTrip(activities, endpoint)
	fmt.Println("suggestionByDate", suggestionByDate)
	fmt.Println("err", err)
	if err != nil {
		return nil, fmt.Errorf("failed to get trip suggestion: %w", err)
	}
	suggestion, err := dto.ConvertToCreateTripRequest(*suggestionByDate)
	if err != nil {
		return nil, fmt.Errorf("failed to convert trip suggestion: %w", err)
	}
	newSuggestionByDate, err := dto.ConvertToCreateTripRequestByDate(suggestion)
	if err != nil {
		return nil, fmt.Errorf("failed to convert trip suggestion: %w", err)
	}
	fmt.Println("Converted suggestion: ", newSuggestionByDate)

	return suggestionByDate, nil
}
