package controller

import (
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
	v1 := router.Group("/api/v1")
	{
		websocket := v1.Group("/ws")
		{
			websocket.POST("/:documentID", wsc.HandleWebSocket)
		}
	}
}

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Replace with proper origin checks in production
	},
}

func (ctrl *WebSocketController) HandleWebSocket(c *gin.Context) {
	documentID := c.Param("documentID")

	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		c.AbortWithStatus(http.StatusBadRequest)
		return
	}

	ctrl.webSocketService.HandleClient(documentID, conn)
}
