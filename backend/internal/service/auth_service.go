package service

import (
	"errors"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"
	"skeleton-internship-backend/internal/util"

	"golang.org/x/crypto/bcrypt"
)

type AuthService interface {
	Register(req dto.RegisterRequest) (*model.User, error)
	Login(username string, password string) (accessToken string, refreshToken string, err error)
	GenerateToken(username string) (accessToken string, refreshToken string, err error)
	Refresh(tokenString string) (newAccessToken string, err error)
}

type authService struct {
	UserRepo repository.UserRepository
}

func NewAuthService(repo repository.UserRepository) AuthService {
	return &authService{UserRepo: repo}
}

// Register and returns JWT tokens.
func (s *authService) Register(req dto.RegisterRequest) (*model.User, error) {
	// Example: fetch user from repository. Assume a method GetByUsername exists.
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	var user = model.User{
		FirstName: req.FirstName,
		LastName:  req.LastName,
		Username:  req.Username,
		Email:     req.Email,
		Password:  string(hashedPassword),
	}

	if err := s.UserRepo.Create(&user); err != nil {
		return nil, err
	}

	user, err = s.UserRepo.GetByUsername(req.Username)
	if err != nil {
		return nil, err
	}

	return &user, nil
}

// Login authenticates the user credentials and returns JWT tokens.
func (s *authService) Login(username string, password string) (accessToken string, refreshToken string, err error) {
	// Example: fetch user from repository. Assume a method GetByUsername exists.
	user, err := s.UserRepo.GetByUsername(username)
	if err != nil {
		return "", "", err
	}

	// Validate password (you might use bcrypt.CompareHashAndPassword here)
	err = util.ValidatePassword(password, user.Password)
	if err != nil {
		return "", "", errors.New(err.Error())
	}

	accessToken, refreshToken, err = s.GenerateToken(user.Username)
	if err != nil {
		return "", "", err
	}
	return accessToken, refreshToken, nil
}

func (s *authService) GenerateToken(username string) (accessToken string, refreshToken string, err error) {
	accessToken, err = util.GenerateAccessToken(username)
	if err != nil {
		return "", "", err
	}

	refreshToken, err = util.GenerateRefreshToken(username)
	if err != nil {
		return "", "", err
	}
	return accessToken, refreshToken, err
}

// Refresh verifies refresh token and creates a new access token.
func (s *authService) Refresh(tokenString string) (newAccessToken string, err error) {
	claims, err := util.ValidateRefreshToken(tokenString)
	if err != nil {
		return "", err
	}

	// Optionally: check if token is blacklisted or revoked
	newAccessToken, err = util.GenerateAccessToken(claims.Username)
	return newAccessToken, err
}
