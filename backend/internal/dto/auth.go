package dto

type RegisterRequest struct {
	FirstName string `json:"first_name"`
	LastName  string `json:"last_name"`
	Email     string `json:"email"`
	Username  string `json:"username"`
	Password  string `json:"password"`
}

type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// TokenResponse represents the structure of the JWT token response.
type TokenResponse struct {
	AccessToken  string `json:"access_token"`            // The access token, used for subsequent requests.
	RefreshToken string `json:"refresh_token,omitempty"` // Optional refresh token, used for obtaining new access tokens.
}
