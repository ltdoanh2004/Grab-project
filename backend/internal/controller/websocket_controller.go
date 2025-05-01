package controller

import (
	"log"
	"net/http"
	"skeleton-internship-backend/internal/service"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

type WebSocketController struct {
	webSocketService *service.WebSocketService
}

func NewWebSocketController(webSocketService *service.WebSocketService) *WebSocketController {
	return &WebSocketController{webSocketService: webSocketService}
}

func (wsc *WebSocketController) RegisterRoutes(router *gin.Engine) {
	log.Println("Registering WebSocket routes")
	v1 := router.Group("/api/v1")
	{
		websocket := v1.Group("/ws")
		{
			websocket.GET("/:documentID", wsc.HandleWebSocket)
		}
	}
}

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Replace with proper origin checks in production
	},
}

func (ctrl *WebSocketController) HandleWebSocket(c *gin.Context) {
	log.Println("HandleWebSocket method invoked")
	documentID := c.Param("documentID")
	log.Printf("Attempting to upgrade connection for documentID: %s", documentID)

	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("Failed to upgrade WebSocket connection: %v", err)
		c.AbortWithStatus(http.StatusBadRequest)
		return
	}

	log.Printf("WebSocket connection established for documentID: %s", documentID)
	ctrl.webSocketService.HandleClient(documentID, conn)
}
