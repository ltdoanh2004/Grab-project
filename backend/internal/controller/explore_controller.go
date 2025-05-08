package controller

import (
	"skeleton-internship-backend/internal/repository"

	"github.com/gin-gonic/gin"
)

type ExploreController struct {
	placeRepository         repository.PlaceRepository
	restaurantRepository    repository.RestaurantRepository
	accommodationRepository repository.AccommodationRepository
}

func NewExploreController(
	placeRepo repository.PlaceRepository,
	restaurantRepo repository.RestaurantRepository,
	accommodationRepo repository.AccommodationRepository,
) *ExploreController {
	return &ExploreController{
		placeRepository:         placeRepo,
		restaurantRepository:    restaurantRepo,
		accommodationRepository: accommodationRepo,
	}
}

func (ec *ExploreController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api/v1")
	{
		explore := v1.Group("/explore")
		{
			explore.GET("/place/:id", ec.getPlaceByID)
			explore.GET("/restaurant/:id", ec.getRestaurantByID)
			explore.GET("/accommodation/:id", ec.getAccommodationByID)
		}
	}
}

func (ec *ExploreController) getPlaceByID(ctx *gin.Context) {
	id := ctx.Param("id")
	place, err := ec.placeRepository.GetByID(id)
	if err != nil {
		ctx.JSON(500, gin.H{"error": "Failed to get place"})
		return
	}
	ctx.JSON(200, place)
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
