package dto

import (
	"skeleton-internship-backend/internal/model"
)

// ExpenseUserDTO represents a user participating in expense splitting
type ExpenseUserDTO struct {
	UserID       string  `json:"user_id"`
	TripID       string  `json:"trip_id"`
	Username     string  `json:"username"`
	CustomAmount float64 `json:"custom_amount,omitempty"` // Amount for custom split
}

// TripExpenseDTO represents an expense for a trip
type TripExpenseDTO struct {
	ExpenseID     string           `json:"expense_id,omitempty"`
	TripID        string           `json:"trip_id"`
	ExpenseName   string           `json:"expense_name"`
	ExpenseType   string           `json:"expense_type"`
	ExpenseAmount float64          `json:"expense_amount"`
	ExpenseDate   string           `json:"expense_date"`
	PaidByUserID  string           `json:"paid_by_user_id"`
	PaidByUser    *model.User      `json:"paid_by_user,omitempty"`
	SplitType     string           `json:"split_type"` // equal, percentage, custom
	ExpenseUsers  []ExpenseUserDTO `json:"expense_users"`
}

// ExpenseBalanceDTO represents the final balance for a user
type ExpenseBalanceDTO struct {
	UserID       string        `json:"user_id"`
	Username     string        `json:"username"`
	TotalPaid    float64       `json:"total_paid"`
	TotalOwed    float64       `json:"total_owed"`
	NetBalance   float64       `json:"net_balance"` // positive means they are owed money, negative means they owe money
	Transactions []Transaction `json:"transactions"`
}

// Transaction represents a payment between two users
type Transaction struct {
	FromUserID   string  `json:"from_user_id"`
	FromUsername string  `json:"from_username"`
	ToUserID     string  `json:"to_user_id"`
	ToUsername   string  `json:"to_username"`
	Amount       float64 `json:"amount"`
}

// TripExpenseSummaryDTO represents a summary of all expenses for a trip
type TripExpenseSummaryDTO struct {
	TripID       string              `json:"trip_id"`
	TripName     string              `json:"trip_name"`
	TotalExpense float64             `json:"total_expense"`
	Expenses     []TripExpenseDTO    `json:"expenses"`
	Balances     []ExpenseBalanceDTO `json:"balances"`
}
