package model

// ExpenseUser represents the association between an expense and a user.
type ExpenseUser struct {
	ExpenseUserID string         `gorm:"type:char(36);primaryKey" json:"expense_user_id"`
	UserID        string         `gorm:"type:char(36);not null" json:"user_id"`
	Outcome       float64        `gorm:"type:decimal(10,2)" json:"outcome"`
	Income        float64        `gorm:"type:decimal(10,2)" json:"income"`
	TripID        string         `gorm:"type:char(36);column:trip_id" json:"trip_id,omitempty"`
	Expenses      []*TripExpense `gorm:"many2many:expense_user_expenses" json:"expenses"`

	// Corrected User relationship
	User *User `json:"user,omitempty"`
}
