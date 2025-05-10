package controller

import (
	"net/http"

	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/service"
	"skeleton-internship-backend/middleware"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type ExpenseController struct {
	expenseService service.ExpenseService
	tripService    service.TripService
}

func NewExpenseController(
	expenseService service.ExpenseService,
	tripService service.TripService,
) *ExpenseController {
	return &ExpenseController{
		expenseService: expenseService,
		tripService:    tripService,
	}
}

func (ec *ExpenseController) RegisterRoutes(router *gin.Engine) {
	v1 := router.Group("/api/v1")
	{
		expense := v1.Group("/expense")
		protected := expense.Group("/")
		protected.Use(middleware.AuthMiddleware())
		{
			// Expense user management
			protected.POST("/user/add", ec.AddExpenseUser)
			protected.GET("/users/:tripId", ec.GetExpenseUsers)

			// Trip expense management
			protected.POST("/add", ec.AddTripExpense)
			protected.GET("/:tripId", ec.GetTripExpenses)

			// Balance calculation
			protected.GET("/balance/:tripId", ec.GetExpenseBalances)
			protected.GET("/summary/:tripId", ec.GetTripExpenseSummary)
		}
	}
}

// AddExpenseUser adds a user to the expense splitting for a trip
// @Summary Add a user to expense splitting
// @Description Add a user to the expense splitting for a trip
// @Tags expense
// @Accept json
// @Produce json
// @Param request body dto.ExpenseUserDTO true "Expense user details"
// @Success 200 {object} map[string]string
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/expense/user/add [post]
func (ec *ExpenseController) AddExpenseUser(ctx *gin.Context) {
	var expenseUser dto.ExpenseUserDTO
	if err := ctx.ShouldBindJSON(&expenseUser); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var err error
	// If username is provided, use it to find the user
	if expenseUser.Username != "" {
		err = ec.expenseService.AddExpenseUserByUsername(expenseUser.TripID, expenseUser.Username)
	} else if expenseUser.UserID != "" {
		// Otherwise use the user ID directly
		err = ec.expenseService.AddExpenseUser(expenseUser.TripID, expenseUser.UserID)
	} else {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Either username or user_id must be provided"})
		return
	}

	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "User added to expense splitting successfully"})
}

// GetExpenseUsers gets all users participating in expense splitting for a trip
// @Summary Get expense users
// @Description Get all users participating in expense splitting for a trip
// @Tags expense
// @Accept json
// @Produce json
// @Param tripId path string true "Trip ID"
// @Success 200 {array} model.ExpenseUser
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/expense/users/{tripId} [get]
func (ec *ExpenseController) GetExpenseUsers(ctx *gin.Context) {
	tripID := ctx.Param("tripId")
	if tripID == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Trip ID is required"})
		return
	}

	expenseUsers, err := ec.expenseService.GetExpenseUsers(tripID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, expenseUsers)
}

// AddTripExpense adds an expense to a trip
// @Summary Add trip expense
// @Description Add an expense to a trip
// @Tags expense
// @Accept json
// @Produce json
// @Param request body dto.TripExpenseDTO true "Trip expense details"
// @Success 200 {object} model.TripExpense
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/expense/add [post]
func (ec *ExpenseController) AddTripExpense(ctx *gin.Context) {
	var expenseDTO dto.TripExpenseDTO
	if err := ctx.ShouldBindJSON(&expenseDTO); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Convert DTO to model
	expense := model.TripExpense{
		ExpenseID:     uuid.New().String(),
		TripID:        expenseDTO.TripID,
		ExpenseName:   expenseDTO.ExpenseName,
		ExpenseType:   expenseDTO.ExpenseType,
		ExpenseAmount: expenseDTO.ExpenseAmount,
		ExpenseDate:   expenseDTO.ExpenseDate,
		PaidByUserID:  expenseDTO.PaidByUserID,
	}

	// Create split expenses based on the split type
	if expenseDTO.SplitType == "equal" {
		// Get all expense users for this trip
		expenseUsers, err := ec.expenseService.GetExpenseUsers(expenseDTO.TripID)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Calculate equal split amount
		splitAmount := expenseDTO.ExpenseAmount / float64(len(expenseUsers))
		expense.SplitExpenses = make([]model.SplitExpense, 0, len(expenseUsers))

		for _, eu := range expenseUsers {
			expense.SplitExpenses = append(expense.SplitExpenses, model.SplitExpense{
				ExpenseID: expense.ExpenseID,
				UserID:    eu.UserID,
				Amount:    splitAmount,
			})
		}
	} else if expenseDTO.SplitType == "custom" {
		// Use custom split amounts
		expense.SplitExpenses = make([]model.SplitExpense, 0, len(expenseDTO.ExpenseUsers))
		for _, eu := range expenseDTO.ExpenseUsers {
			expense.SplitExpenses = append(expense.SplitExpenses, model.SplitExpense{
				ExpenseID: expense.ExpenseID,
				UserID:    eu.UserID,
			})
		}
	}

	// Add the expense
	result, err := ec.expenseService.AddTripExpense(&expense)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, result)
}

// GetTripExpenses gets all expenses for a trip
// @Summary Get trip expenses
// @Description Get all expenses for a trip
// @Tags expense
// @Accept json
// @Produce json
// @Param tripId path string true "Trip ID"
// @Success 200 {array} model.TripExpense
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/expense/{tripId} [get]
func (ec *ExpenseController) GetTripExpenses(ctx *gin.Context) {
	tripID := ctx.Param("tripId")
	if tripID == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Trip ID is required"})
		return
	}

	expenses, err := ec.expenseService.GetTripExpenses(tripID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, expenses)
}

// GetExpenseBalances gets the balance for each user in a trip
// @Summary Get expense balances
// @Description Get the balance for each user in a trip
// @Tags expense
// @Accept json
// @Produce json
// @Param tripId path string true "Trip ID"
// @Success 200 {array} dto.ExpenseBalanceDTO
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/expense/balance/{tripId} [get]
func (ec *ExpenseController) GetExpenseBalances(ctx *gin.Context) {
	tripID := ctx.Param("tripId")
	if tripID == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Trip ID is required"})
		return
	}

	balances, err := ec.expenseService.CalculateBalances(tripID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, balances)
}

// GetTripExpenseSummary gets a summary of all expenses for a trip
// @Summary Get trip expense summary
// @Description Get a summary of all expenses for a trip
// @Tags expense
// @Accept json
// @Produce json
// @Param tripId path string true "Trip ID"
// @Success 200 {object} dto.TripExpenseSummaryDTO
// @Failure 400 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/v1/expense/summary/{tripId} [get]
func (ec *ExpenseController) GetTripExpenseSummary(ctx *gin.Context) {
	tripID := ctx.Param("tripId")
	if tripID == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Trip ID is required"})
		return
	}

	// Get trip details
	trip, err := ec.tripService.GetTrip(tripID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	summary, err := ec.expenseService.GetTripExpenseSummary(tripID, trip.TripName)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, summary)
}
