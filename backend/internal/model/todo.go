package model

import (
	"time"
)

// Todo represents a todo item in the system
// @Description Todo represents a single todo item with its details
type Todo struct {
	// Unique identifier of the todo
	ID uint `json:"id" gorm:"primaryKey" example:"1"`

	// Title of the todo item
	Title string `json:"title" gorm:"not null" example:"Complete project documentation"`

	// Detailed description of the todo item
	Description string `json:"description" example:"Write comprehensive documentation for the API endpoints"`

	// Current status of the todo item (pending, in-progress, completed)
	Status string `json:"status" gorm:"default:pending" example:"pending" enums:"pending,in-progress,completed"`

	// Timestamp when the todo was created
	CreatedAt time.Time `json:"created_at" example:"2024-03-15T08:00:00Z"`

	// Timestamp when the todo was last updated
	UpdatedAt time.Time `json:"updated_at" example:"2024-03-15T08:00:00Z"`
}
