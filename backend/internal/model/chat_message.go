package model

type ChatMessage struct {
	Sender     string `json:"sender"`
	DocumentID string `json:"documentId"`
	Content    string `json:"content"` // whole doc or diff
}
