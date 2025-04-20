package util

import (
	"skeleton-internship-backend/config"
	"time"

	"github.com/golang-jwt/jwt"
)

// AccessClaims represents the JWT claims for the access token.
type AccessClaims struct {
	Username string `json:"username"`
	jwt.StandardClaims
}

// RefreshClaims represents the JWT claims for the refresh token.
type RefreshClaims struct {
	Username string `json:"username"`
	jwt.StandardClaims
}

// GenerateAccessToken creates a JWT access token.
func GenerateAccessToken(username string) (string, error) {
	claims := AccessClaims{
		Username: username,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: time.Now().Add(config.AppConfig.Token.AccessTokenTTL).Unix(),
			IssuedAt:  time.Now().Unix(),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(config.AppConfig.Token.AccessTokenSecret))
}

// GenerateRefreshToken creates a JWT refresh token.
func GenerateRefreshToken(username string) (string, error) {
	claims := RefreshClaims{
		Username: username,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: time.Now().Add(config.AppConfig.Token.RefreshTokenTTL).Unix(),
			IssuedAt:  time.Now().Unix(),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(config.AppConfig.Token.RefreshTokenSecret))
}

// ValidateAccessToken validates the access token and returns its claims.
func ValidateAccessToken(tokenString string) (*AccessClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &AccessClaims{}, func(token *jwt.Token) (interface{}, error) {
		return config.AppConfig.Token.AccessTokenSecret, nil
	})
	if err != nil {
		return nil, err
	}

	claims, ok := token.Claims.(*AccessClaims)
	if !ok || !token.Valid {
		return nil, err
	}

	return claims, nil
}

// ValidateRefreshToken validates the refresh token and returns its claims.
func ValidateRefreshToken(tokenString string) (*RefreshClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &RefreshClaims{}, func(token *jwt.Token) (interface{}, error) {
		return config.AppConfig.Token.RefreshTokenSecret, nil
	})
	if err != nil {
		return nil, err
	}

	claims, ok := token.Claims.(*RefreshClaims)
	if !ok || !token.Valid {
		return nil, err
	}

	return claims, nil
}
