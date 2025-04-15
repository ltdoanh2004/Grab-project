package model

// Response is a generic response structure for API endpoints
type Response struct {
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// NewResponse creates a new Response instance
func NewResponse(message string, data interface{}) *Response {
	return &Response{
		Message: message,
		Data:    data,
	}
}
