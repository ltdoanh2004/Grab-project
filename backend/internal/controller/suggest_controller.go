package controller

import (
	"net/http"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"
	"skeleton-internship-backend/middleware"
	"github.com/gin-gonic/gin"
)

type SuggestController struct {
	suggestSerivce service.SuggestService
	tripService    service.TripService
}

func NewSuggestController(
	suggestService service.SuggestService,
	tripService service.TripService,
) *SuggestController {
	return &SuggestController{
		suggestSerivce: suggestService,
		tripService:    tripService,
	}
}

func (sc *SuggestController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api/v1")
	{
		suggestion := v1.Group("/suggest")
		protected := suggestion.Group("/")
		protected.Use(middleware.AuthMiddleware())
		{
			protected.POST("/accommodations", sc.SuggestAccommodations)
			protected.POST("/places", sc.SuggestPlaces)
			protected.POST("/restaurants", sc.SuggestRestaurants)
			protected.POST("/trip", sc.SuggestTrip)
			protected.POST("/comment", sc.SuggestWithComment)
		}
		detail := v1.Group("/detail")
		{
			detail.GET("/place/:id", sc.GetPlaceByID)
			detail.GET("/restaurant/:id", sc.GetRestaurantByID)
			detail.GET("/accommodation/:id", sc.GetAccommodationByID)
		}
	}
}

// SuggestAccommodations godoc
// @Summary Suggest accommodations
// @Description Get accommodation suggestions based on travel preferences
// @Tags suggest
// @Accept json
// @Produce json
// @Param preference body model.TravelPreference true "Travel Preferences"
// @Success 200 {object} model.Response{data=[]dto.ActivityDetail}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/suggest/accommodations [post]
func (sc *SuggestController) SuggestAccommodations(ctx *gin.Context) {
	travelPreference := &model.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input: "+err.Error(), nil))
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestAccommodations(travelPreference)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get accommodation suggestions: "+err.Error(), nil))
		return
	}
	activities := []dto.ActivityDetail{}
	for _, accommodation := range suggestion.Accommodations {
		activities = append(activities, accommodation.ToActivityDetail())
	}

	ctx.JSON(http.StatusOK, model.NewResponse("Success", activities))
}

// SuggestPlaces godoc
// @Summary Suggest places
// @Description Get activity suggestions based on travel preferences
// @Tags suggest
// @Accept json
// @Produce json
// @Param preference body model.TravelPreference true "Travel Preferences"
// @Success 200 {object} model.Response{data=[]dto.ActivityDetail}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/suggest/places [post]
func (sc *SuggestController) SuggestPlaces(ctx *gin.Context) {
	travelPreference := &model.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input: "+err.Error(), nil))
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestPlaces(travelPreference)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get activity suggestions: "+err.Error(), nil))
		return
	}
	activities := []dto.ActivityDetail{}
	for _, place := range suggestion.Places {
		activities = append(activities, place.ToActivityDetail())
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Success", activities))
}

// SuggestRestaurants godoc
// @Summary Suggest restaurants
// @Description Get restaurant suggestions based on travel preferences
// @Tags suggest
// @Accept json
// @Produce json
// @Param preference body model.TravelPreference true "Travel Preferences"
// @Success 200 {object} model.Response{data=[]dto.ActivityDetail}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/suggest/restaurants [post]
func (sc *SuggestController) SuggestRestaurants(ctx *gin.Context) {
	travelPreference := &model.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input: "+err.Error(), nil))
		return
	}
	suggestion, err := sc.suggestSerivce.SuggestRestaurants(travelPreference)

	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get restaurant suggestions: "+err.Error(), nil))
		return
	}
	activities := []dto.ActivityDetail{}
	for _, restaurant := range suggestion.Restaurants {
		activities = append(activities, restaurant.ToActivityDetail())
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Success", activities))
}

// SuggestTrip godoc
// @Summary Suggest trip
// @Description Get comprehensive suggestions based on travel preferences for accommodations, places, and restaurants
// @Tags suggest
// @Accept json
// @Produce json
// @Param preference body model.TravelPreference true "Travel Preferences"
// @Success 200 {object} model.Response{data=dto.TripDTOByDate} "Suggested trip"
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/suggest/trip [post]
func (sc *SuggestController) SuggestTrip(ctx *gin.Context) {
	travelPreference := &model.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input: "+err.Error(), nil))
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestAll(travelPreference)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get suggestions: "+err.Error(), nil))
		return
	}
	getPlanEndpoint := "/api/v1/suggest/trip"
	// Extract userID from access_token
	userID, exists := ctx.Get("user_id")
	if !exists {
		ctx.JSON(http.StatusUnauthorized, model.Response{
			Message: "Unauthorized: userID not found in access_token",
			Data:    nil,
		})
		return
	}

	var suggestedTrip *dto.TripDTOByDate
	suggestedTrip, err = sc.tripService.SuggestTrip(userID.(string), *suggestion, getPlanEndpoint)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to get trip suggestion: " + err.Error(),
			Data:    nil,
		})
		return
	}

	_, err = sc.tripService.CreateTravelPreference(suggestedTrip.TripID, travelPreference)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to create travel preference: " + err.Error(),
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Trip suggestion retrieved successfully",
		Data:    suggestedTrip,
	})
}

// GetPlaceByID godoc
// @Summary Get place details by ID
// @Description Retrieve detailed information about a specific place
// @Tags detail
// @Accept json
// @Produce json
// @Param id path string true "Place ID"
// @Success 200 {object} model.Response{data=dto.ActivityDetail}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/detail/place/{id} [get]
func (sc *SuggestController) GetPlaceByID(ctx *gin.Context) {
	id := ctx.Param("id")
	placeDetail, err := sc.suggestSerivce.GetPlaceByID(id)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get place details: "+err.Error(), nil))
		return
	}

	placeSuggestion := dto.PlaceSuggestion{
		PlaceID:       placeDetail.PlaceID,
		DestinationID: placeDetail.DestinationID,
		Name:          placeDetail.Name,
		URL:           placeDetail.URL,
		Address:       placeDetail.Address,
		Duration:      placeDetail.Duration,
		Type:          placeDetail.Type,
		Images:        placeDetail.Images,
		MainImage:     placeDetail.MainImage,
		Price:         placeDetail.Price,
		Rating:        placeDetail.Rating,
		Description:   placeDetail.Description,
		OpeningHours:  placeDetail.OpeningHours,
		Reviews:       placeDetail.Reviews,
		Categories:    placeDetail.Categories,
		Unit:          placeDetail.Unit,
	}

	activityDetail := placeSuggestion.ToActivityDetail()
	ctx.JSON(http.StatusOK, model.NewResponse("Success", activityDetail))
}

// GetRestaurantByID godoc
// @Summary Get restaurant details by ID
// @Description Retrieve detailed information about a specific restaurant
// @Tags detail
// @Accept json
// @Produce json
// @Param id path string true "Restaurant ID"
// @Success 200 {object} model.Response{data=dto.ActivityDetail}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/detail/restaurant/{id} [get]
func (sc *SuggestController) GetRestaurantByID(ctx *gin.Context) {
	id := ctx.Param("id")
	restaurantDetail, err := sc.suggestSerivce.GetRestaurantByID(id)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get restaurant details: "+err.Error(), nil))
		return
	}

	restaurantSuggestion := dto.RestaurantSuggestion{
		RestaurantID:  restaurantDetail.RestaurantID,
		DestinationID: restaurantDetail.DestinationID,
		Name:          restaurantDetail.Name,
		Address:       restaurantDetail.Address,
		Rating:        restaurantDetail.Rating,
		Phone:         restaurantDetail.Phone,
		PhotoURL:      restaurantDetail.PhotoURL,
		URL:           restaurantDetail.URL,
		Location:      restaurantDetail.Location,
		Reviews:       restaurantDetail.Reviews,
		Services:      restaurantDetail.Services,
		IsDelivery:    restaurantDetail.IsDelivery,
		IsBooking:     restaurantDetail.IsBooking,
		IsOpening:     restaurantDetail.IsOpening,
		PriceRange:    restaurantDetail.PriceRange,
		Description:   restaurantDetail.Description,
		Cuisines:      restaurantDetail.Cuisines,
		OpeningHours:  restaurantDetail.OpeningHours,
	}

	activityDetail := restaurantSuggestion.ToActivityDetail()
	ctx.JSON(http.StatusOK, model.NewResponse("Success", activityDetail))
}

// GetAccommodationByID godoc
// @Summary Get accommodation details by ID
// @Description Retrieve detailed information about a specific accommodation
// @Tags detail
// @Accept json
// @Produce json
// @Param id path string true "Accommodation ID"
// @Success 200 {object} model.Response{data=dto.ActivityDetail}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/detail/accommodation/{id} [get]
func (sc *SuggestController) GetAccommodationByID(ctx *gin.Context) {
	id := ctx.Param("id")
	accommodationDetail, err := sc.suggestSerivce.GetAccommodationByID(id)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get accommodation details: "+err.Error(), nil))
		return
	}

	accommodationSuggestion := dto.AccommodationSuggestion{
		AccommodationID: accommodationDetail.AccommodationID,
		DestinationID:   accommodationDetail.DestinationID,
		Name:            accommodationDetail.Name,
		Location:        accommodationDetail.Location,
		City:            accommodationDetail.City,
		Price:           accommodationDetail.Price,
		Rating:          accommodationDetail.Rating,
		Description:     accommodationDetail.Description,
		Link:            accommodationDetail.Link,
		Images:          accommodationDetail.Images,
		RoomTypes:       accommodationDetail.RoomTypes,
		RoomInfo:        accommodationDetail.RoomInfo,
		Unit:            accommodationDetail.Unit,
		TaxInfo:         accommodationDetail.TaxInfo,
		ElderlyFriendly: accommodationDetail.ElderlyFriendly,
	}

	activityDetail := accommodationSuggestion.ToActivityDetail()
	ctx.JSON(http.StatusOK, model.NewResponse("Success", activityDetail))
}

// SuggestWithComment godoc
// @Summary Suggest by comment
// @Description Get suggestions based on travel preference and comment activity using AI
// @Tags suggest
// @Accept json
// @Produce json
// @Param data body dto.SuggestWithCommentRequest true "Suggest with Comment Request"
// @Success 200 {object} model.Response{data=dto.SuggestWithCommentResponse}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/suggest/comment [post]
func (sc *SuggestController) SuggestWithComment(ctx *gin.Context) {
	var req dto.SuggestWithCommentRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input: "+err.Error(), nil))
		return
	}

	response, err := sc.suggestSerivce.SuggestWithComment(&req)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get comment suggestions: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Success", response))
}
