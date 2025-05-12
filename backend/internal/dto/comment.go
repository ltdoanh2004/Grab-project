package dto

type Comment struct {
	CommentMessage string `json:"comment_message"`
	ActivityID     string `json:"activity_id"`
	Type           string `json:"type"`
}
