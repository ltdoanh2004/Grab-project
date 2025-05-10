package model

// TripExpense represents an expense associated with a trip.
type TripExpense struct {
	ExpenseID     string         `gorm:"type:char(36);primaryKey" json:"expense_id"`
	TripID        string         `gorm:"type:char(36);not null" json:"trip_id"`
	ExpenseName   string         `gorm:"not null" json:"expense_name"`
	ExpenseType   string         `json:"expense_type"`
	ExpenseAmount float64        `gorm:"type:decimal(10,2)" json:"expense_amount"`
	ExpenseDate   string         `json:"expense_date"`
	PaidByUserID  string         `gorm:"type:char(36);column:paid_by_user_id" json:"paid_by_user_id,omitempty"`
	SplitExpenses []SplitExpense `gorm:"type:json" json:"split_expenses,omitempty"`

	PaidByUser *User `gorm:"foreignKey:PaidByUserID" json:"paid_by_user,omitempty"`

	// Updated association
	ExpenseUsers []ExpenseUser `gorm:"many2many:expense_user_expenses;" json:"expense_users,omitempty"`
}

type SplitExpense struct {
	ExpenseID string  `json:"expense_id"`
	UserID    string  `json:"user_id"`
	Amount    float64 `json:"amount"`
}
