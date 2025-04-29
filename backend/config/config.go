package config

import (
	"time"

	"github.com/rs/zerolog/log"
	"github.com/spf13/viper"
)

// Config holds the overall configuration for the application
type Config struct {
	Server   ServerConfig   // Server-related configuration
	Database DatabaseConfig // Database-related configuration
	Token    TokenConfig    // Token-related configuration
	AI       AIConfig       // AI service-related configuration
}

// ServerConfig holds server-specific configuration
type ServerConfig struct {
	Port string // Port on which the server will run
}

// DatabaseConfig holds database-specific configuration
type DatabaseConfig struct {
	Host     string // Database host address
	Port     string // Database port
	User     string // Database username
	Password string // Database password
	Name     string // Database name
}

type AIConfig struct {
	Host string // AI service host address
	Port string // AI service port
}

// TokenConfig holds token-related configuration
type TokenConfig struct {
	AccessTokenSecret  string        // Secret key for signing access tokens
	RefreshTokenSecret string        // Secret key for signing refresh tokens
	AccessTokenTTL     time.Duration // Time-to-live for access tokens
	RefreshTokenTTL    time.Duration // Time-to-live for refresh tokens
}

var AppConfig Config

// NewConfig initializes and loads the application configuration
func NewConfig() (*Config, error) {
	// Configure Viper to read .env file
	viper.SetConfigName(".env") // Name of the config file (without extension)
	viper.SetConfigType("env")  // Type of the config file
	viper.AddConfigPath(".")    // Path to look for the config file in the current directory

	// Enable automatic environment variable loading
	viper.AutomaticEnv()

	// Read config file
	if err := viper.ReadInConfig(); err != nil {
		// Log a warning if the config file cannot be read
		log.Warn().Err(err).Msg("Error reading config file")
	}

	var config Config
	// Load server configuration
	config.Server.Port = viper.GetString("SERVER_PORT")

	// Load database configuration
	config.Database.Host = viper.GetString("DATABASE_HOST")
	config.Database.Port = viper.GetString("DATABASE_PORT")
	config.Database.User = viper.GetString("DATABASE_USER")
	config.Database.Password = viper.GetString("DATABASE_PASSWORD")
	config.Database.Name = viper.GetString("DATABASE_NAME")

	// Load token configuration
	config.Token.AccessTokenSecret = viper.GetString("ACCESS_TOKEN_SECRET")
	config.Token.RefreshTokenSecret = viper.GetString("REFRESH_TOKEN_SECRET")
	config.Token.AccessTokenTTL = time.Minute * time.Duration(viper.GetUint("ACCESS_TOKEN_TTL"))
	config.Token.RefreshTokenTTL = time.Hour * 24 * time.Duration(viper.GetUint("REFRESH_TOKEN_TTL"))

	// Load AI configuration
	config.AI.Host = viper.GetString("AI_HOST")
	config.AI.Port = viper.GetString("AI_PORT")

	// Log the loaded configuration
	log.Info().Interface("config", config).Msg("Config loaded")

	AppConfig = config
	return &config, nil
}
