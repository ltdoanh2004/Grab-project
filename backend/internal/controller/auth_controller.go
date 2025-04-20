package controller

import (
	"net/http"

	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"

	"github.com/gin-gonic/gin"
)

// AuthController handles authentication-related HTTP requests.
type AuthController struct {
	authService service.AuthService
}

// NewAuthController creates a new instance of AuthController.
func NewAuthController(authService service.AuthService) *AuthController {
	return &AuthController{
		authService: authService,
	}
}

func (ac *AuthController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api")
	{
		todos := v1.Group("/auth")
		{
			todos.POST("/login", ac.Login)
			todos.POST("/register", ac.Register)
		}
	}
}

// Register handles user registration requests.
func (ac *AuthController) Register(ctx *gin.Context) {
	var registerRequest dto.RegisterRequest

	// Bind the JSON payload to the RegisterRequest struct.
	if err := ctx.ShouldBindJSON(&registerRequest); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid request payload", nil))
		return
	}

	// Call the authService to handle registration logic.
	user, err := ac.authService.Register(registerRequest)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Register failed: "+err.Error(), nil))
		return
	}

	accessToken, refreshToken, err := ac.authService.GenerateToken(user.Username)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Generate token failed: "+err.Error(), nil))
		return
	}

	// Create a response containing the generated tokens.
	tokenResponse := dto.TokenResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
	}

	// Respond with the tokenResponse in JSON format.
	ctx.JSON(http.StatusOK, model.NewResponse("Register successfully", tokenResponse))
}

// Login handles user login requests.
func (ac *AuthController) Login(ctx *gin.Context) {
	var loginRequest dto.LoginRequest

	// Bind the JSON payload to the LoginRequest struct.
	if err := ctx.ShouldBindJSON(&loginRequest); err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Invalid request payload", nil))
		return
	}

	// Call the authService to authenticate the user and generate tokens.
	accessToken, refreshToken, err := ac.authService.Login(loginRequest.Username, loginRequest.Password)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, model.NewResponse("Login falied: "+err.Error(), nil))
		return
	}

	// Create a response containing the generated tokens.
	tokenResponse := dto.TokenResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
	}

	// Respond with the tokenResponse in JSON format.
	ctx.JSON(http.StatusOK, model.NewResponse("Login successfully", tokenResponse))
}
