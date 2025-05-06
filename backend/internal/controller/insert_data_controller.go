package controller

import (
	"net/http"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"

	"github.com/gin-gonic/gin"
	_ "github.com/swaggo/files"       // Swagger files
	_ "github.com/swaggo/gin-swagger" // Swagger middleware
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

// @Summary Insert Destination Data
// @Description Import destination data from a CSV file
// @Tags InsertData
// @Accept json
// @Produce json
// @Success 200 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/insert_csv/destination [post]
func (x *InsertDataController) InsertDestinationCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertDestinationData("./mockdata/city_processed.csv")
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to import data from CSV: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Destinations data imported successfully", nil))

}

// @Summary Insert Hotel Data
// @Description Import hotel data from a CSV file
// @Tags InsertData
// @Accept json
// @Produce json
// @Success 200 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/insert_csv/hotel [post]
func (x *InsertDataController) InsertHotelCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertHotelData("./mockdata/hotel_processed.csv")
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to import data from CSV: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Hotels data imported successfully", nil))
}

// @Summary Insert Place Data
// @Description Import place data from a CSV file
// @Tags InsertData
// @Accept json
// @Produce json
// @Success 200 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/insert_csv/place [post]
func (x *InsertDataController) InsertPlaceCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertPlaceData("./mockdata/place_processed.csv")
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to import data from CSV: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Places data imported successfully", nil))
}

// @Summary Insert Restaurant Data
// @Description Import restaurant data from a CSV file
// @Tags InsertData
// @Accept json
// @Produce json
// @Success 200 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/insert_csv/restaurant [post]
func (x *InsertDataController) InsertRestaurantCSV(ctx *gin.Context) {
	err := x.insertDataService.InsertRestaurantData("./mockdata/fnb_processed.csv")
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to import data from CSV: "+err.Error(), nil))
		return
	}
	ctx.JSON(http.StatusOK, model.NewResponse("Restaurants data imported successfully", nil))
}
