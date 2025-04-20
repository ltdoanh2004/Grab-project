package util

import (
	"fmt"

	"golang.org/x/crypto/bcrypt"
)

// return the bcrypt hash of the password
func HashPassword(password string) (string, error) {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", fmt.Errorf("failed to hash password: %w", err)
	}
	return string(hashedPassword), nil
}

func ValidatePassword(password string, hashedPassword string) error {
	if len(hashedPassword) < 60 {
		return fmt.Errorf("invalid hashed password format or length")
	}
	return bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
}
