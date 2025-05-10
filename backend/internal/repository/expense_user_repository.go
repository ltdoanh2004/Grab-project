package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

type ExpenseUserRepository interface {
	AddExpenseUsers(expenseUsers []model.ExpenseUser) error
	GetExpenseUsersByTripID(tripID string) ([]model.ExpenseUser, error)
	UpdateExpenseUser(expenseUser model.ExpenseUser) error
	DeleteExpenseUser(expenseUserID string) error
	GetByExpenseIDAndUserID(expenseID string, userID string) (*model.ExpenseUser, error)
}

type GormExpenseUserRepository struct {
	db *gorm.DB
}

func NewExpenseUserRepository(db *gorm.DB) ExpenseUserRepository {
	return &GormExpenseUserRepository{db: db}
}

func (r *GormExpenseUserRepository) AddExpenseUsers(expenseUsers []model.ExpenseUser) error {
	return r.db.Create(&expenseUsers).Error
}

func (r *GormExpenseUserRepository) GetExpenseUsersByTripID(tripID string) ([]model.ExpenseUser, error) {
	var expenseUsers []model.ExpenseUser
	// Directly query expense_users using trip_id
	err := r.db.Where("trip_id = ?", tripID).Find(&expenseUsers).Error
	return expenseUsers, err
}

func (r *GormExpenseUserRepository) UpdateExpenseUser(expenseUser model.ExpenseUser) error {
	return r.db.Save(&expenseUser).Error
}

func (r *GormExpenseUserRepository) DeleteExpenseUser(expenseUserID string) error {
	return r.db.Delete(&model.ExpenseUser{}, "expense_user_id = ?", expenseUserID).Error
}

func (r *GormExpenseUserRepository) GetByExpenseIDAndUserID(expenseID string, userID string) (*model.ExpenseUser, error) {
	var expenseUser model.ExpenseUser
	err := r.db.Joins("JOIN expense_user_expenses ON expense_user_expenses.expense_user_id = expense_users.expense_user_id").
		Where("expense_user_expenses.expense_id = ? AND expense_users.user_id = ?", expenseID, userID).
		First(&expenseUser).Error
	if err != nil {
		return nil, err
	}
	return &expenseUser, nil
}
