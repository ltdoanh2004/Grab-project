package controller

import (
	"fmt"
	"net/http"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

type WebSocketController struct {
	service *service.WebSocketService
}

func NewWebSocketController(service *service.WebSocketService) *WebSocketController {
	return &WebSocketController{service: service}
}

func (wsc *WebSocketController) RegisterRoutes(router *gin.Engine) {
	ws := router.Group("/ws")
	{
		ws.GET("/:id", wsc.HandleWebSocket)
	}
}

func (c *WebSocketController) HandleWebSocket(ctx *gin.Context) {
	fmt.Println("hello")
	// Extract group ID from URL
	tripID := ctx.Param("id")
	if tripID == "" {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid trip ID: ID cannot be empty",
			Data:    nil,
		})
		return
	}

	// Upgrade connection to WebSocket
	conn, err := upgrader.Upgrade(ctx.Writer, ctx.Request, nil)
	if err != nil {
		ctx.String(http.StatusInternalServerError, "Failed to upgrade connection")
		return
	}

	// Get the hub for the group
	hub := c.service.GetHub(tripID)

	// Register the connection with the hub
	hub.Register <- conn // Updated to use exported field

	// Handle incoming messages
	go func() {
		defer func() {
			hub.Unregister <- conn // Updated to use exported field
		}()
		for {
			_, message, err := conn.ReadMessage()
			if err != nil {
				break
			}
			hub.Broadcast <- message // Updated to use exported field
		}
	}()
}
