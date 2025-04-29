package controller

import (
	"net/http"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"

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
		{
			suggestion.GET("/accommodations", sc.SuggestAccommodations)
			suggestion.GET("/places", sc.SuggestPlaces)
			suggestion.GET("/restaurants", sc.SuggestRestaurants)
			suggestion.GET("/all", sc.SuggestAll)
		}
	}
}

// SuggestAccommodations godoc
// @Summary Suggest accommodations
// @Description Get accommodation suggestions based on travel preferences
// @Tags suggest
// @Accept json
// @Produce json
// @Param preference body dto.TravelPreference true "Travel Preferences"
// @Success 200 {object} model.Response{data=dto.AccommodationsSuggestion}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/suggest/accommodations [get]
func (sc *SuggestController) SuggestAccommodations(ctx *gin.Context) {
	travelPreference := &dto.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input: "+err.Error(), nil))
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestAccommodations(travelPreference)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get accommodation suggestions: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Success", suggestion))
}

// SuggestPlaces godoc
// @Summary Suggest places
// @Description Get activity suggestions based on travel preferences
// @Tags suggest
// @Accept json
// @Produce json
// @Param preference body dto.TravelPreference true "Travel Preferences"
// @Success 200 {object} model.Response{data=dto.PlacesSuggestion}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/suggest/places [get]
func (sc *SuggestController) SuggestPlaces(ctx *gin.Context) {
	travelPreference := &dto.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input: "+err.Error(), nil))
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestPlaces(travelPreference)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get activity suggestions: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Success", suggestion))
}

// SuggestRestaurants godoc
// @Summary Suggest restaurants
// @Description Get restaurant suggestions based on travel preferences
// @Tags suggest
// @Accept json
// @Produce json
// @Param preference body dto.TravelPreference true "Travel Preferences"
// @Success 200 {object} model.Response{data=dto.RestaurantsSuggestion}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/suggest/restaurants [get]
func (sc *SuggestController) SuggestRestaurants(ctx *gin.Context) {
	travelPreference := &dto.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input: "+err.Error(), nil))
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestRestaurants(travelPreference)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get restaurant suggestions: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Success", suggestion))
}

// SuggestRestaurants godoc
// @Summary Suggest restaurants
// @Description Get restaurant suggestions based on travel preferences
// @Tags suggest
// @Accept json
// @Produce json
// @Param preference body dto.TravelPreference true "Travel Preferences"
// @Success 200 {object} model.Response{data=dto.RestaurantsSuggestion}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/suggest/restaurants [get]
func (sc *SuggestController) SuggestAll(ctx *gin.Context) {
	travelPreference := &dto.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input: "+err.Error(), nil))
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestAll(travelPreference)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to get restaurant suggestions: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Success", suggestion))
}
