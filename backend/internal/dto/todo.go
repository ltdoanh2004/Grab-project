package dto

// TodoCreate represents the data structure for creating a new todo
// @Description Todo creation request body
type TodoCreate struct {
	// Title of the todo item
	Title string `json:"title" example:"Complete project documentation" binding:"required"`

	// Detailed description of the todo item
	Description string `json:"description" example:"Write comprehensive documentation for the API endpoints"`

	// Current status of the todo item (pending, in-progress, completed)
	Status string `json:"status" example:"pending" enums:"pending,in-progress,completed"`
}
