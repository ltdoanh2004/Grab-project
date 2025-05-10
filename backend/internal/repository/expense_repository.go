package repository

import (
	"skeleton-internship-backend/internal/model"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

type ExpenseRepository interface {
	AddTripExpenses(expenses []model.TripExpense) error
	AddTripExpense(expense model.TripExpense) (model.TripExpense, error)
	GetExpensesByTripID(tripID string) ([]model.TripExpense, error)
	UpdateExpenseUsers(expenseUsers []model.ExpenseUser) error
}

type GormExpenseRepository struct {
	db *gorm.DB
}

func NewExpenseRepository(db *gorm.DB) ExpenseRepository {
	return &GormExpenseRepository{db: db}
}

func (r *GormExpenseRepository) AddTripExpenses(expenses []model.TripExpense) error {
	return r.db.Create(&expenses).Error
}

func (r *GormExpenseRepository) AddTripExpense(expense model.TripExpense) (model.TripExpense, error) {
	expense.ExpenseID = uuid.New().String()
	if err := r.db.Create(expense).Error; err != nil {
		return model.TripExpense{}, err
	}
	return expense, nil
}

func (r *GormExpenseRepository) GetExpensesByTripID(tripID string) ([]model.TripExpense, error) {
	var expenses []model.TripExpense
	err := r.db.Where("trip_id = ?", tripID).Find(&expenses).Error
	return expenses, err
}

func (r *GormExpenseRepository) UpdateExpenseUsers(expenseUsers []model.ExpenseUser) error {
	return r.db.Save(&expenseUsers).Error
}
