package controller

import (
	"skeleton-internship-backend/internal/repository"

	"github.com/gin-gonic/gin"
)

type ExploreController struct {
	activityRepository      repository.ActivityRepository
	restaurantRepository    repository.RestaurantRepository
	accommodationRepository repository.AccommodationRepository
}

func NewExploreController(
	activityRepo repository.ActivityRepository,
	restaurantRepo repository.RestaurantRepository,
	accommodationRepo repository.AccommodationRepository,
) *ExploreController {
	return &ExploreController{
		activityRepository:      activityRepo,
		restaurantRepository:    restaurantRepo,
		accommodationRepository: accommodationRepo,
	}
}

func (ec *ExploreController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api/v1")
	{
		explore := v1.Group("/explore")
		{
			explore.POST("/activity", ec.getActivityByID)
			explore.POST("/restaurant", ec.getRestaurantByID)
			explore.POST("/accommodation", ec.getAccommodationByID)
		}
	}
}

func (ec *ExploreController) getActivityByID(ctx *gin.Context) {
	id := ctx.Param("id")
	activity, err := ec.activityRepository.GetByID(id)
	if err != nil {
		ctx.JSON(500, gin.H{"error": "Failed to get activity"})
		return
	}
	ctx.JSON(200, activity)
}

func (ec *ExploreController) getRestaurantByID(ctx *gin.Context) {
	id := ctx.Param("id")
	restaurant, err := ec.restaurantRepository.GetByID(id)
	if err != nil {
		ctx.JSON(500, gin.H{"error": "Failed to get restaurant"})
		return
	}
	ctx.JSON(200, restaurant)
}

func (ec *ExploreController) getAccommodationByID(ctx *gin.Context) {
	id := ctx.Param("id")
	accommodation, err := ec.accommodationRepository.GetByID(id)
	if err != nil {
		ctx.JSON(500, gin.H{"error": "Failed to get accommodation"})
		return
	}
	ctx.JSON(200, accommodation)
}
