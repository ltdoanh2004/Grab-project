package main

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
	"go.uber.org/fx"

	"skeleton-internship-backend/config"
	"skeleton-internship-backend/database"
	_ "skeleton-internship-backend/docs" // This will be created by swag
	"skeleton-internship-backend/internal/controller"
	"skeleton-internship-backend/internal/logger"
	"skeleton-internship-backend/internal/repository"
	"skeleton-internship-backend/internal/service"
)

// @title           Todo List API
// @version         1.0
// @description     A modern RESTful API for managing your todos efficiently. This API provides comprehensive endpoints for creating, reading, updating, and deleting todo items.
// @termsOfService  http://swagger.io/terms/

// @contact.name   API Support Team
// @contact.url    http://www.example.com/support
// @contact.email  support@example.com

// @license.name  MIT
// @license.url   https://opensource.org/licenses/MIT

// @host      localhost:8080
// @BasePath  /api/v1
// @schemes   http https

// @tag.name         todos
// @tag.description  Operations about todos
// @tag.docs.url     http://example.com/docs/todos
// @tag.docs.description Detailed information about todo operations

// @tag.name         health
// @tag.description  API health check operations

// @securityDefinitions.apikey Bearer
// @in header
// @name Authorization
// @description Enter the token with the `Bearer: ` prefix, e.g. "Bearer abcde12345".

func main() {
	app := fx.New(
		fx.Provide(
			NewConfig,
			database.NewDB,
			NewGinEngine,
			repository.NewRepository,
			service.NewService,
			controller.NewController,
		),
		fx.Invoke(RegisterRoutes),
	)

	app.Run()
}

func NewConfig() (*config.Config, error) {
	return config.NewConfig()
}

func NewGinEngine() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	r := gin.New()
	r.Use(gin.Recovery())

	// Configure CORS
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"}, // Add your frontend URLs
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Add swagger route
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	return r
}

func RegisterRoutes(
	lifecycle fx.Lifecycle,
	router *gin.Engine,
	cfg *config.Config,
	controller *controller.Controller,
) {
	controller.RegisterRoutes(router)
	logger.Init()

	server := &http.Server{
		Addr:    ":" + cfg.Server.Port,
		Handler: router,
	}

	lifecycle.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			log.Info().Msgf("Starting server on port %s", cfg.Server.Port)
			go func() {
				if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
					log.Fatal().Err(err).Msg("Failed to start server")
				}
			}()
			return nil
		},
		OnStop: func(ctx context.Context) error {
			log.Info().Msg("Shutting down server")
			return server.Shutdown(ctx)
		},
	})
}
