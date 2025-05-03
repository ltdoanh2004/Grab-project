package controller

import (
	"net/http"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"

	"github.com/gin-gonic/gin"
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
			insert_csv.POST("destination", c.InsertDestinationCSV)
			insert_csv.POST("hotel", c.InsertHotelCSV)
			insert_csv.POST("place", c.InsertPlaceCSV)
			insert_csv.POST("restaurant", c.InsertRestaurantCSV)
		}
	}
}

func (x *InsertDataController) InsertDestinationCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertDestinationData("./mockdata/city_processed.csv")
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to import data from CSV: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Destinations data imported successfully", nil))

}

func (x *InsertDataController) InsertHotelCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertHotelData("./mockdata/hotel_processed.csv")
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to import data from CSV: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Hotels data imported successfully", nil))
}

func (x *InsertDataController) InsertPlaceCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertPlaceData("./mockdata/place_processed.csv")
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to import data from CSV: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Places data imported successfully", nil))
}

func (x *InsertDataController) InsertRestaurantCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertRestaurantData("./mockdata/fnb_processed.csv")
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to import data from CSV: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Restaurants data imported successfully", nil))
}
