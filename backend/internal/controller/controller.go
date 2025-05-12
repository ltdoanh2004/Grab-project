package controller

import (
	"net/http"
	"strconv"

	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"
)

type Controller struct {
	service service.Service
}

func NewController(service service.Service) *Controller {
	return &Controller{
		service: service,
	}
}

func (c *Controller) RegisterRoutes(router *gin.Engine) {
	router.GET("/health", c.HealthCheck)
	v1 := router.Group("/api/v1")
	{
		todos := v1.Group("/todos")
		{
			todos.GET("", c.GetAllTodos)
			todos.GET("/:id", c.GetTodoByID)
			todos.POST("", c.CreateTodo)
			todos.PUT("/:id", c.UpdateTodo)
			todos.DELETE("/:id", c.DeleteTodo)
		}
	}
}

// HealthCheck godoc
// @Summary Show the status of server.
// @Description get the status of server.
// @Tags health
// @Accept */*
// @Produce json
// @Success 200 {object} model.Response
// @Router /health [get]
func (x *Controller) HealthCheck(ctx *gin.Context) {
	log.Info().Msg("Health check")
	ctx.JSON(http.StatusOK, model.NewResponse("OK", nil))
}

// GetAllTodos godoc
// @Summary Get all todos
// @Description get all todos
// @Tags todos
// @Accept json
// @Produce json
// @Success 200 {object} model.Response{data=[]model.Todo}
// @Failure 500 {object} model.Response
// @Router /api/v1/todos [get]
func (c *Controller) GetAllTodos(ctx *gin.Context) {
	todos, err := c.service.GetAllTodos()
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to fetch todos", nil))
		return
	}

	ctx.JSON(http.StatusOK, model.NewResponse("Todos fetched successfully", todos))
}

// GetTodoByID godoc
// @Summary Get a todo
// @Description get todo by ID
// @Tags todos
// @Accept json
// @Produce json
// @Param id path int true "Todo ID"
// @Success 200 {object} model.Response{data=model.Todo}
// @Failure 400 {object} model.Response
// @Failure 404 {object} model.Response
// @Router /api/v1/todos/{id} [get]
func (c *Controller) GetTodoByID(ctx *gin.Context) {
	id, err := strconv.ParseUint(ctx.Param("id"), 10, 32)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid ID format", nil))
		return
	}

	todo, err := c.service.GetTodoByID(uint(id))
	if err != nil {
		ctx.JSON(http.StatusNotFound, model.NewResponse("Todo not found", nil))
		return
	}

	ctx.JSON(http.StatusOK, model.NewResponse("Todo fetched successfully", todo))
}

// CreateTodo godoc
// @Summary Create a todo
// @Description create new todo
// @Tags todos
// @Accept json
// @Produce json
// @Param todo body dto.TodoCreate true "Create todo"
// @Success 201 {object} model.Response{data=model.Todo}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/todos [post]
func (c *Controller) CreateTodo(ctx *gin.Context) {
	var input dto.TodoCreate
	if err := ctx.ShouldBindJSON(&input); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input", nil))
		return
	}

	todo, err := c.service.CreateTodo(&input)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to create todo", nil))
		return
	}

	ctx.JSON(http.StatusCreated, model.NewResponse("Todo created successfully", todo))
}

// UpdateTodo godoc
// @Summary Update a todo
// @Description update todo by ID
// @Tags todos
// @Accept json
// @Produce json
// @Param id path int true "Todo ID"
// @Param todo body dto.TodoCreate true "Update todo"
// @Success 200 {object} model.Response{data=model.Todo}
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/todos/{id} [put]
func (c *Controller) UpdateTodo(ctx *gin.Context) {
	id, err := strconv.ParseUint(ctx.Param("id"), 10, 32)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid ID format", nil))
		return
	}

	var input dto.TodoCreate
	if err := ctx.ShouldBindJSON(&input); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid input", nil))
		return
	}

	todo, err := c.service.UpdateTodo(uint(id), &input)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to update todo", nil))
		return
	}

	ctx.JSON(http.StatusOK, model.NewResponse("Todo updated successfully", todo))
}

// DeleteTodo godoc
// @Summary Delete a todo
// @Description delete todo by ID
// @Tags todos
// @Accept json
// @Produce json
// @Param id path int true "Todo ID"
// @Success 200 {object} model.Response
// @Failure 400 {object} model.Response
// @Failure 500 {object} model.Response
// @Router /api/v1/todos/{id} [delete]
func (c *Controller) DeleteTodo(ctx *gin.Context) {
	id, err := strconv.ParseUint(ctx.Param("id"), 10, 32)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid ID format", nil))
		return
	}

	if err := c.service.DeleteTodo(uint(id)); err != nil {
		ctx.JSON(http.StatusInternalServerError, model.NewResponse("Failed to delete todo", nil))
		return
	}

	ctx.JSON(http.StatusOK, model.NewResponse("Todo deleted successfully", nil))
}
