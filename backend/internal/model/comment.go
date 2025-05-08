package model

// Comment represents a comment associated with a trip entity.
type Comment struct {
	CommentID      string `gorm:"type:char(36);primaryKey" json:"comment_id"`
	UserID         string `gorm:"type:char(36);not null" json:"user_id"`
	CommentMessage string `gorm:"column:comment_message;size:255" json:"comment_message"`

	TripRestaurantID    string `gorm:"type:char(36);column:trip_restaurant_id" json:"trip_restaurant_id,omitempty"`
	TripAccommodationID string `gorm:"type:char(36);column:trip_accommodation_id" json:"trip_accommodation_id,omitempty"`
	TripPlaceID         string `gorm:"type:char(36);column:trip_place_id" json:"trip_place_id,omitempty"`
}
