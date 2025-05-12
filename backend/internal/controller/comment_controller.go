package controller

import (
	"net/http"
	"skeleton-internship-backend/internal/dto"
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
				protected.GET("/activity/:id", cc.GetCommentsByActivityID)
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
// @Param comment body dto.Comment true "Comment Details"
// @Success 200 {object} model.Response{data=model.Comment} "Returns comment"
// @Failure 400 {object} model.Response "Invalid request"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/comment/create [post]
func (cc *CommentController) CreateComment(ctx *gin.Context) {
	var request dto.Comment
	if err := ctx.ShouldBindJSON(&request); err != nil {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid request body: " + err.Error(),
			Data:    nil,
		})
		return
	}
	userID, exists := ctx.Get("user_id")
	if !exists {
		ctx.JSON(http.StatusUnauthorized, model.Response{
			Message: "Unauthorized: userID not found in access_token",
			Data:    nil,
		})
		return
	}

	comment, err := cc.commentService.AddComment(&request, userID.(string))
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, model.Response{
			Message: "Failed to create comment: " + err.Error(),
			Data:    nil,
		})
		return
	}

	ctx.JSON(http.StatusOK, model.Response{
		Message: "Comment created successfully",
		Data:    comment,
	})
}

// GetCommentsByActivityID godoc
// @Summary Get comments by activity ID
// @Description Get all comments for a specific activity
// @Tags comment
// @Accept json
// @Produce json
// @Param id path string true "Activity ID"
// @Success 200 {object} model.Response{data=model.Comment} "Comments for the activity"
// @Failure 400 {object} model.Response "Invalid activity ID"
// @Failure 500 {object} model.Response "Internal server error"
// @Router /api/v1/comment/activity/{id} [get]
func (cc *CommentController) GetCommentsByActivityID(ctx *gin.Context) {
	activityID := ctx.Param("id")
	if activityID == "" {
		ctx.JSON(http.StatusBadRequest, model.Response{
			Message: "Invalid activity ID: ID cannot be empty",
			Data:    nil,
		})
		return
	}

	comments, err := cc.commentService.GetCommentsByActivityID(activityID)
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
