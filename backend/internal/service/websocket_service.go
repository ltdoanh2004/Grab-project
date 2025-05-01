package service

import (
	"encoding/json"
	"fmt"
	"sync"

	"skeleton-internship-backend/internal/model"

	"github.com/gorilla/websocket"
)

// Client represents a websocket connection and its outbound channel.
type Client struct {
	Conn *websocket.Conn
	Send chan []byte
}

// Hub manages a set of Clients and broadcasts messages.
type Hub struct {
	clients    map[*Client]bool
	broadcast  chan []byte
	register   chan *Client
	unregister chan *Client
}

// NewHub creates and returns a new Hub.
func NewHub() *Hub {
	return &Hub{
		clients:    make(map[*Client]bool),
		broadcast:  make(chan []byte),
		register:   make(chan *Client),
		unregister: make(chan *Client),
	}
}

// run starts the main loop for the Hub.
func (h *Hub) run() {
	for {
		select {
		case client := <-h.register:
			h.addClient(client)

		case client := <-h.unregister:
			h.removeClient(client)

		case message := <-h.broadcast:
			h.sendToClients(message)
		}
	}
}

func (h *Hub) addClient(client *Client) {
	h.clients[client] = true
}

func (h *Hub) removeClient(client *Client) {
	if _, ok := h.clients[client]; ok {
		delete(h.clients, client)
		close(client.Send)
	}
}

func (h *Hub) sendToClients(message []byte) {
	for client := range h.clients {
		select {
		case client.Send <- message:
		default:
			h.removeClient(client)
		}
	}
}

// WebSocketService manages multiple Hubs.
type WebSocketService struct {
	hubs map[string]*Hub
	mu   sync.RWMutex
}

// NewWebSocketService creates a new WebSocketService.
func NewWebSocketService() *WebSocketService {
	return &WebSocketService{
		hubs: make(map[string]*Hub),
	}
}

// getOrCreateHub returns an existing Hub for the documentID or creates a new one.
func (s *WebSocketService) getOrCreateHub(documentID string) *Hub {
	s.mu.Lock()
	defer s.mu.Unlock()

	if hub, exists := s.hubs[documentID]; exists {
		return hub
	}

	hub := NewHub()
	s.hubs[documentID] = hub
	go hub.run()
	return hub
}

// HandleClient upgrades the connection for a document and starts read/write goroutines.
func (s *WebSocketService) HandleClient(documentID string, conn *websocket.Conn) {
	client := &Client{
		Conn: conn,
		Send: make(chan []byte),
	}
	hub := s.getOrCreateHub(documentID)
	hub.register <- client

	go s.readPump(hub, client)
	go s.writePump(client)
}

// readPump reads incoming messages from the connection and broadcasts them.
func (s *WebSocketService) readPump(hub *Hub, client *Client) {
	defer func() {
		hub.unregister <- client
		client.Conn.Close()
	}()

	for {
		if _, message, err := client.Conn.ReadMessage(); err == nil {
			var parsed model.ChatMessage
			if err := json.Unmarshal(message, &parsed); err != nil {
				fmt.Println("Invalid message:", err)
				continue
			}
			hub.broadcast <- message
		} else {
			break
		}
	}
}

// writePump writes messages from the send channel to the websocket connection.
func (s *WebSocketService) writePump(client *Client) {
	for message := range client.Send {
		if err := client.Conn.WriteMessage(websocket.TextMessage, message); err != nil {
			break
		}
	}
}
