package controller

import (
	"net/http"

	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"
	"skeleton-internship-backend/middleware"

	"github.com/gin-gonic/gin"
)

type TripController struct {
	tripService service.TripService
}

func NewTripController(
	tripService service.TripService,
) *TripController {
	return &TripController{
		tripService: tripService,
	}
}

func (tc *TripController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api/v1")
	{
		trip := v1.Group("/trip")
		{
			// This endpoint doesn't require middleware
			trip.GET("/:id", tc.GetTrip)

			// Other endpoints require authentication
			protected := trip.Group("/")
			protected.Use(middleware.AuthMiddleware())
			{
				protected.GET("/me", tc.GetTripsByUserID)
				protected.POST("/create", tc.CreateTrip)
				protected.PUT("/save", tc.SaveTrip)
				protected.POST("/get_plan", tc.GetPlan)
				protected.PUT("/activity", tc.UpdateActivity)
			}
		}
	}
}

// CreateTrip godoc
// @Summary Create a new trip
// @Description Create a new trip with destinations, accommodations, activities, and restaurants
// @Tags trip
// @Accept json
// @Produce json
// @Param trip body dto.TripDTO true "Trip Details"
// @Success 200 {object} model.Response{data=string} "Returns trip ID"
// @Failure 400 {object} model.Response "Invalid request"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/trip/create [post]
func (tc *TripController) CreateTrip(ctx *gin.Context) {
	var request dto.TripDTO
	if err := ctx.ShouldBindJSON(&request); err != nil {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid request body: " + err.Error(),
			Data:    nil,
		})
		return
	}

	tripID, err := tc.tripService.CreateTrip(&request)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to create trip: " + err.Error(),
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Trip created successfully",
		Data:    tripID,
	})
}

// SaveTrip godoc
// @Summary Save changes to an existing trip
// @Description Update an existing trip with new details including destinations, accommodations, activities, and restaurants
// @Tags trip
// @Accept json
// @Produce json
// @Param trip body dto.TripDTOByDate true "Trip Details"
// @Success 200 {object} model.Response "Trip updated successfully"
// @Failure 400 {object} model.Response "Invalid request"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/trip/save [put]
func (tc *TripController) SaveTrip(ctx *gin.Context) {
	var request dto.TripDTOByDate
	if err := ctx.ShouldBindJSON(&request); err != nil {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid request body: " + err.Error(),
			Data:    nil,
		})
		return
	}

	userID, exists := ctx.Get("user_id")
	if !exists {
		ctx.JSON(http.StatusUnauthorized, model.Response{
			Message: "Unauthorized: userID not found in access_token",
			Data:    nil,
		})
		return
	}
	if userID.(string) != request.UserID {
		ctx.JSON(http.StatusUnauthorized, model.Response{
			Message: "Unauthorized: userID in access_token does not match the trip's userID",
			Data:    nil,
		})
		return
	}

	if err := tc.tripService.SaveTrip(&request); err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to save trip: " + err.Error(),
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Trip saved successfully",
		Data:    request.TripID,
	})
}

// GetTrip godoc
// @Summary Get trip details
// @Description Get complete trip details including destinations, accommodations, activities, and restaurants
// @Tags trip
// @Accept json
// @Produce json
// @Param id path string true "Trip ID"
// @Success 200 {object} model.Response{data=dto.TripDTOByDate} "Trip details"
// @Failure 400 {object} model.Response "Invalid trip ID"
// @Failure 404 {object} model.Response "Trip not found"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/trip/{id} [get]
func (tc *TripController) GetTrip(ctx *gin.Context) {
	tripID := ctx.Param("id")
	if tripID == "" {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid trip ID: ID cannot be empty",
			Data:    nil,
		})
		return
	}

	trip, err := tc.tripService.GetTrip(tripID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to get trip: " + err.Error(),
			Data:    nil,
		})
		return
	}

	if trip == nil {
		ctx.JSON(http.StatusNotFound, model.Response{
			Message: "Trip not found",
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Trip retrieved successfully",
		Data:    trip,
	})
}

// SuggestTrip godoc
// @Summary Get trip suggestions
// @Description Get AI-generated trip suggestions based on user preferences
// @Tags trip
// @Accept json
// @Produce json
// @Param request body dto.TripSuggestionRequest true "Trip Suggestion Parameters"
// @Success 200 {object} model.Response{data=dto.TripDTOByDate} "Suggested trip"
// @Failure 400 {object} model.Response "Invalid request"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/trip/get_plan [post]
func (tc *TripController) GetPlan(ctx *gin.Context) {
	endpoints := "/api/v1/suggest/trip"
	var request dto.TripSuggestionRequest
	if err := ctx.ShouldBindJSON(&request); err != nil {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid request body: " + err.Error(),
			Data:    nil,
		})
		return
	}

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
	suggestedTrip, err := tc.tripService.SuggestTrip(userID.(string), request, endpoints)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to get trip suggestion: " + err.Error(),
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Trip suggestion retrieved successfully",
		Data:    suggestedTrip,
	})
}

// UpdateActivity godoc
// @Summary Update an activity
// @Description Update an activity (accommodation, restaurant, or place) based on its type
// @Tags trip
// @Accept json
// @Produce json
// @Param request body dto.Activity true "Updated Activity Data"
// @Success 200 {object} model.Response "Activity updated successfully"
// @Failure 400 {object} model.Response "Invalid request"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/trip/activity [put]
func (tc *TripController) UpdateActivity(ctx *gin.Context) {
	var updatedData dto.Activity
	if err := ctx.ShouldBindJSON(&updatedData); err != nil {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid request body: " + err.Error(),
			Data:    nil,
		})
		return
	}

	if err := tc.tripService.UpdateActivity(updatedData.Type, updatedData.ActivityID, updatedData); err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to update activity: " + err.Error(),
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Activity updated successfully",
		Data:    nil,
	})
}

// GetTripsByUserID godoc
// @Summary Get trips by user ID
// @Description Retrieve all trips associated with the authenticated user
// @Tags trip
// @Accept json
// @Produce json
// @Success 200 {object} model.Response{data=[]dto.TripDTOByDate} "List of trips"
// @Failure 400 {object} model.Response "Invalid request"
// @Failure 404 {object} model.Response "No trips found"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/trip/me [get]
func (tc *TripController) GetTripsByUserID(ctx *gin.Context) {
	// Extract userID from access token
	userID, exists := ctx.Get("user_id")
	if !exists {
		ctx.JSON(http.StatusUnauthorized, model.Response{
			Message: "Unauthorized: userID not found in access_token",
			Data:    nil,
		})
		return
	}

	trips, err := tc.tripService.GetTripsByUserID(userID.(string))
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to retrieve trips: " + err.Error(),
			Data:    nil,
		})
		return
	}

	if len(trips) == 0 {
		ctx.JSON(http.StatusNotFound, model.Response{
			Message: "No trips found for the authenticated user",
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Trips retrieved successfully",
		Data:    trips,
	})
}
