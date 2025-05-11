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
	suggestion.DestinationID = travelPreference.DestinationID
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
		"/api/v1/fix/activity",
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
	fmt.Println("body", string(body))
	return body, nil
}

// SuggestWithComment calls the AI service for comment-based suggestions,
// receives the JSON response, parses it into SuggestWithCommentResponse and returns it.
func (ss *suggestService) SuggestWithComment(req *dto.SuggestWithCommentRequest) (*dto.SuggestWithCommentResponse, error) {
	// jsonResponse, err := ss.callAISuggestWithComment(req)
	jsonResponse, err := ss.mockCallSuggestWithCommentAPI(req)
	if err != nil {
		return nil, err
	}

	var aiResponse dto.SuggestWithCommentResponse
	if err := json.Unmarshal(jsonResponse, &aiResponse); err != nil {
		return nil, fmt.Errorf("failed to decode AI service response: %w", err)
	}
	suggestionList := []dto.Activity{}
	for i := range aiResponse.SuggestionList {
		suggestion := aiResponse.SuggestionList[i]
		suggestion.ID = aiResponse.SuggestionList[i].ID
		suggestion.Type = aiResponse.SuggestionType
		suggestion.ActivityID = req.Activity.ActivityID
		suggestion.StartTime = req.Activity.StartTime
		suggestion.EndTime = req.Activity.EndTime
		suggestionList = append(suggestionList, suggestion)
	}
	aiResponse.SuggestionList = suggestionList
	fmt.Println("aiResponse: ", aiResponse)
	return &aiResponse, nil
}

// mockCallSuggestWithCommentAPI provides mock JSON data for the comment-based suggestion API.
func (ss *suggestService) mockCallSuggestWithCommentAPI(req *dto.SuggestWithCommentRequest) ([]byte, error) {
	mockJSON := `
{
  "suggestion_type": "place",
  "suggestion_list": [
    {
      "id": "place_000881",
      "name": "Bảo tàng Phụ nữ Việt Nam",
      "description": "Bảo tàng Phụ nữ Việt Nam, tọa lạc tại trung tâm Hà Nội, là một trong những điểm đến hấp dẫn cho cả gia đình và du khách tìm hiểu về vai trò của phụ nữ trong lịch sử và văn hóa Việt Nam. Một trong những điểm độc đáo của bảo tàng là các khu vực tương tác hiện đại, cho phép trẻ em và người lớn tham gia trải nghiệm, khám phá thông qua hoạt động thực tế thay vì chỉ xem tranh ảnh. \n\nBảo tàng sở hữu những triển lãm thân thiện với gia đình, giúp trẻ em dễ dàng tiếp cận thông tin một cách thú vị và sinh động. Với thời gian tham quan ngắn, nơi đây trở thành lựa chọn tối ưu cho những ai bị hạn chế về thời gian nhưng vẫn mong muốn tìm hiểu văn hóa phong phú của đất nước.\n\nĐặc biệt, Bảo tàng Phụ nữ Việt Nam giải quyết những mối quan tâm của nhiều du khách về tính thân thiện và hợp thời cho trẻ em, đáp ứng nhu cầu khám phá và học hỏi của cả người lớn và trẻ nhỏ. Thay vì đến Bảo tàng Lịch sử Quốc gia, nơi có thể thiên về thông tin hàn lâm và không gian rộng lớn, Bảo tàng Phụ nữ mang đến trải nghiệm gần gũi và dễ tiếp cận hơn với mọi lứa tuổi. Đây chính là điểm nhấn làm nên sự đặc biệt của địa điểm này trong",
      "price_ai_estimate": 80000.0
    },
    {
      "id": "place_001117",
      "name": "Bảo tàng Dân tộc học Việt Nam",
      "description": "Bảo tàng Dân tộc học Việt Nam nằm ở Hà Nội, là một điểm đến hấp dẫn cho những ai muốn tìm hiểu về văn hóa và phong tục tập quán của các dân tộc Việt Nam. Bảo tàng không chỉ trưng bày các hiện vật quý giá mà còn có những mô hình tương tác sống động, giúp du khách trải nghiệm chân thực hơn về đời sống dân gian. Điểm đặc biệt là không gian ngoài trời rộng rãi, nơi trẻ em có thể tự do khám phá và vui chơi, tạo điều kiện lý tưởng cho gia đình đến tham quan.\n\nSo với Bảo tàng Lịch sử Quốc gia, Bảo tàng Dân tộc học mang lại trải nghiệm phong phú hơn về văn hóa dân tộc đa dạng của Việt Nam. Các khu vực trưng bày được phân chia rõ ràng theo từng dân tộc, từ trang phục, phong tục tập quán đến nhạc cụ và nghệ thuật dân gian, giúp du khách dễ dàng nắm bắt và hiểu biết sâu sắc hơn về mỗi nền văn hóa.\n\nNgoài ra, bảo tàng cũng chú trọng đến việc giải quyết những băn khoăn của du khách như sự tương tác và học hỏi cho trẻ em, bằng cách đưa vào các hoạt động thực hành và trò chơi dân gian. Nơi đây thực sự là một lựa chọn tuyệt vời cho những ai muốn trải nghiệm văn hóa Việt Nam một cách gần gũi và thú",
      "price_ai_estimate": 150000.0
    },
    {
      "id": "place_000594",
      "name": "Khu vui chơi Thiên đường Bảo Sơn",
      "description": "**Khu vui chơi Thiên đường Bảo Sơn** tại Hà Nội là một địa điểm hấp dẫn tuyệt vời cho cả gia đình, đặc biệt là trẻ em. Nằm trong khuôn viên rộng lớn, nơi đây kết hợp giữa những khu vui chơi giải trí sôi động và bảo tàng tương tác giáo dục. Một trong những điểm nổi bật của Thiên đường Bảo Sơn là không gian tương tác, nơi trẻ em có thể tham gia vào nhiều hoạt động thực tế để khám phá các khía cạnh văn hóa, lịch sử và khoa học một cách sống động.\n\nChọn Khu vui chơi Thiên đường Bảo Sơn làm điểm đến thay cho Bảo tàng Lịch sử Quốc gia không chỉ vì không khí vui tươi, mà còn bởi tính giáo dục thực tiễn mà nó mang lại cho trẻ em. Tại đây, trẻ em có thể học hỏi qua các trò chơi và trải nghiệm thực tế, giúp củng cố kiến thức một cách tự nhiên mà không thấy chán.\n\nNgoài ra, khu vui chơi cũng đã chú trọng cải thiện những vấn đề được người dùng nêu trong các bình luận. Những hoạt động được tổ chức theo chủ đề, không gian sạch sẽ và an toàn, cùng với sự hướng dẫn nhiệt tình từ đội ngũ nhân viên, giúp giải quyết các mối bận tâm của phụ huynh về sự an toàn và chất lượng trải nghiệm cho trẻ em. Thiên đường Bảo Sơn thực sự",
      "price_ai_estimate": 400000.0
    }
  ],
  "query_used": "Thời gian tham quan ngắn hơn, Môi trường thân thiện với gia đình"
}
`
	return []byte(mockJSON), nil
}
