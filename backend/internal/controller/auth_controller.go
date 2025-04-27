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
	authService       service.AuthService
	insertDataService service.InsertDataService
}

// NewAuthController creates a new instance of AuthController.
func NewAuthController(
	authService service.AuthService,
	insertDataService service.InsertDataService,
) *AuthController {
	return &AuthController{
		authService:       authService,
		insertDataService: insertDataService,
	}
}

func (ac *AuthController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api/v1")
	{
		todos := v1.Group("/auth")
		{
			todos.POST("/login", ac.Login)
			todos.POST("/register", ac.Register)
		}
	}
}

// Authentication godoc
// @Summary User registration
// @Description handles user registration requests
// @Tags auth
// @Accept json
// @Produce json
// @Param register body dto.RegisterRequest true "Register"
// @Success 200 {object} model.Response{data=[]dto.TokenResponse}
// @Failure 400 {object} model.Response
// @Router /api/v1/auth/register [post]
func (ac *AuthController) Register(ctx *gin.Context) {
	var registerRequest dto.RegisterRequest
	// ac.insertDataService.ReadCSV("../data/hotel_processed.csv")

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

	accessToken, refreshToken, err := ac.authService.GenerateToken(user.UserID)
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

// Login godoc
// @Summary User login
// @Description handles user login requests
// @Tags auth
// @Accept json
// @Produce json
// @Param login body dto.LoginRequest true "Login"
// @Success 200 {object} model.Response{data=[]dto.TokenResponse}
// @Failure 400 {object} model.Response
// @Router /api/v1/auth/login [post]
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
