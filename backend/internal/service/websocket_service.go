package service

import (
	"fmt"
	"sync"

	"github.com/gorilla/websocket"
)

type Hub struct {
	clients    map[*websocket.Conn]bool
	Broadcast  chan []byte          // Exported
	Register   chan *websocket.Conn // Exported
	Unregister chan *websocket.Conn // Exported
}

func NewHub() *Hub {
	return &Hub{
		clients:    make(map[*websocket.Conn]bool),
		Broadcast:  make(chan []byte),
		Register:   make(chan *websocket.Conn),
		Unregister: make(chan *websocket.Conn),
	}
}

func (h *Hub) Run() {
	for {
		select {
		case conn := <-h.Register: // Updated to use exported field
			h.clients[conn] = true
		case conn := <-h.Unregister: // Updated to use exported field
			if _, ok := h.clients[conn]; ok {
				delete(h.clients, conn)
				conn.Close()
			}
		case message := <-h.Broadcast: // Updated to use exported field
			for conn := range h.clients {
				fmt.Println(message)
				conn.WriteMessage(websocket.TextMessage, message)
			}
		}
	}
}

type WebSocketService struct {
	hubs map[string]*Hub
	mu   sync.Mutex
}

func NewWebSocketService() *WebSocketService {
	return &WebSocketService{
		hubs: make(map[string]*Hub),
	}
}

func (s *WebSocketService) GetHub(groupID string) *Hub {
	s.mu.Lock()
	defer s.mu.Unlock()

	if hub, exists := s.hubs[groupID]; exists {
		return hub
	}

	hub := NewHub()
	s.hubs[groupID] = hub
	go hub.Run()
	return hub
}
