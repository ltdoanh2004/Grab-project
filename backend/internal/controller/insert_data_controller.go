package controller

import (
	"skeleton-internship-backend/internal/service"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"
)

type InsertDataController struct {
	insertDataService service.InsertDataService
}

func NewInsertDataController(insertDataService service.InsertDataService) *InsertDataController {
	return &InsertDataController{
		insertDataService: insertDataService,
	}
}

func (c *InsertDataController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api/v1")
	{
		insert_csv := v1.Group("/insert_csv")
		{
			insert_csv.POST("hotel", c.InsertHotelCSV)
			insert_csv.POST("place", c.InsertPlaceCSV)
			insert_csv.POST("restaurant", c.InsertRestaurantCSV)
		}
	}
}
func (x *InsertDataController) InsertHotelCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertHotelData("./mockdata/hotel_processed.csv")
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to import data from CSV")
	}
	log.Info().Msg("Hotel data imported successfully")
}

func (x *InsertDataController) InsertPlaceCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertPlaceData("./mockdata/place_processed.csv")
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to import data from CSV")
	}
	log.Info().Msg("Place data imported successfully")
}

func (x *InsertDataController) InsertRestaurantCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertRestaurantData("./mockdata/fnb_processed.csv")
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to import data from CSV")
	}
	log.Info().Msg("Restaurant data imported successfully")
}
