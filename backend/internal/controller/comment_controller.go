package controller

import (
	"net/http"

	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"
	"skeleton-internship-backend/middleware"

	"github.com/gin-gonic/gin"
)

type CommentController struct {
	commentService service.CommentService
}

func NewCommentController(
	commentService service.CommentService,
) *CommentController {
	return &CommentController{
		commentService: commentService,
	}
}

func (cc *CommentController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api/v1")
	{
		comment := v1.Group("/comment")
		{
			// Other endpoints require authentication
			protected := comment.Group("/")
			protected.Use(middleware.AuthMiddleware())
			{
				protected.POST("/create", cc.CreateComment)
				protected.GET("/trip/:id", cc.GetCommentsByTripID)
			}
		}
	}
}

// CreateComment godoc
// @Summary Create a new comment
// @Description Create a new comment
// @Tags comment
// @Accept json
// @Produce json
// @Param comment body model.Comment true "Comment Details"
// @Success 200 {object} model.Response{data=string} "Returns comment ID"
// @Failure 400 {object} model.Response "Invalid request"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/comment/create [post]
func (cc *CommentController) CreateComment(ctx *gin.Context) {
	var request model.Comment
	if err := ctx.ShouldBindJSON(&request); err != nil {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid request body: " + err.Error(),
			Data:    nil,
		})
		return
	}

	commentID, err := cc.commentService.AddComment(&request)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to create comment: " + err.Error(),
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Comment created successfully",
		Data:    commentID,
	})
}

// GetCommentsByTripID godoc
// @Summary Get comments by trip ID
// @Description Get all comments for a specific trip
// @Tags comment
// @Accept json
// @Produce json
// @Param id path string true "Trip ID"
// @Success 200 {object} model.Response{data=model.Comment} "Comments for the trip"
// @Failure 400 {object} model.Response "Invalid trip ID"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/comment/trip/{id} [get]
func (cc *CommentController) GetCommentsByTripID(ctx *gin.Context) {
	tripID := ctx.Param("id")
	if tripID == "" {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid trip ID: ID cannot be empty",
			Data:    nil,
		})
		return
	}

	comments, err := cc.commentService.GetCommentsByTripID(tripID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to get comments: " + err.Error(),
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Comments retrieved successfully",
		Data:    comments,
	})
}
