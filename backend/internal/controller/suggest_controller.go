package controller

import (
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/service"

	"github.com/gin-gonic/gin"
)

type SuggestController struct {
	suggestSerivce service.SuggestService
}

func NewSuggestController(
	suggestService service.SuggestService,
) *SuggestController {
	return &SuggestController{
		suggestSerivce: suggestService,
	}
}

func (sc *SuggestController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api/v1")
	{
		suggestion := v1.Group("/suggest")
		{
			suggestion.POST("/accommodations", sc.SuggestAccommodations)
			suggestion.POST("/activities", sc.SuggestActivities)
			suggestion.POST("/restaurants", sc.SuggestRestaurants)
		}
	}
}

func (sc *SuggestController) SuggestAccommodations(ctx *gin.Context) {
	travelPreference := &dto.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(400, gin.H{"error": "Invalid input"})
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestAccommodations(travelPreference)
	if err != nil {
		ctx.JSON(500, gin.H{"error": "Failed to get accommodation suggestions"})
		return
	}
	ctx.JSON(200, suggestion)
}

func (sc *SuggestController) SuggestActivities(ctx *gin.Context) {
	travelPreference := &dto.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(400, gin.H{"error": "Invalid input"})
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestActivities(travelPreference)
	if err != nil {
		ctx.JSON(500, gin.H{"error": "Failed to get activity suggestions"})
		return
	}
	ctx.JSON(200, suggestion)
}

func (sc *SuggestController) SuggestRestaurants(ctx *gin.Context) {
	travelPreference := &dto.TravelPreference{}
	if err := ctx.ShouldBindJSON(travelPreference); err != nil {
		ctx.JSON(400, gin.H{"error": "Invalid input"})
		return
	}

	suggestion, err := sc.suggestSerivce.SuggestRestaurants(travelPreference)
	if err != nil {
		ctx.JSON(500, gin.H{"error": "Failed to get restaurant suggestions"})
		return
	}
	ctx.JSON(200, suggestion)
}
