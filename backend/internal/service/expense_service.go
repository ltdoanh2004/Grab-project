package service

import (
	"errors"
	"math"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"

	"github.com/google/uuid"
)

type ExpenseService interface {
	// Trip expense management
	AddTripExpense(expense *model.TripExpense) (model.TripExpense, error)
	AddTripExpenses(expenses []model.TripExpense) error
	GetTripExpenses(tripID string) ([]model.TripExpense, error)
	GetExpensesByTripID(tripID string) ([]model.TripExpense, error)

	// Expense splitting
	SplitExpense(expense *model.TripExpense) error
	SplitExpenses(expenses []model.TripExpense) error

	// Expense users management
	AddExpenseUser(tripID string, userID string) error
	AddExpenseUserByUsername(tripID string, username string) error
	GetExpenseUsers(tripID string) ([]model.ExpenseUser, error)

	// Balance calculation
	CalculateBalances(tripID string) ([]dto.ExpenseBalanceDTO, error)
	GetTripExpenseSummary(tripID string, tripName string) (*dto.TripExpenseSummaryDTO, error)
}

type expenseService struct {
	expenseRepository     repository.ExpenseRepository
	expenseUserRepository repository.ExpenseUserRepository
	userRepository        repository.UserRepository
	tripRepository        repository.TripRepository
}

func NewExpenseService(
	expenseRepo repository.ExpenseRepository,
	expenseUserRepo repository.ExpenseUserRepository,
	userRepo repository.UserRepository,
	tripRepo repository.TripRepository,
) ExpenseService {
	return &expenseService{
		expenseRepository:     expenseRepo,
		expenseUserRepository: expenseUserRepo,
		userRepository:        userRepo,
		tripRepository:        tripRepo,
	}
}

func (es *expenseService) AddTripExpense(expense *model.TripExpense) (model.TripExpense, error) {
	// Generate UUID if not provided
	if expense.ExpenseID == "" {
		expense.ExpenseID = uuid.New().String()
	}

	// Add the expense to the database
	if err := es.expenseRepository.AddTripExpenses([]model.TripExpense{*expense}); err != nil {
		return *expense, err
	}

	// Split the expense among users
	if err := es.SplitExpense(expense); err != nil {
		return *expense, err
	}

	return *expense, nil
}

func (es *expenseService) AddTripExpenses(expenses []model.TripExpense) error {
	// Generate UUIDs for expenses if not provided
	for i := range expenses {
		if expenses[i].ExpenseID == "" {
			expenses[i].ExpenseID = uuid.New().String()
		}
	}

	// Add expenses to the database
	if err := es.expenseRepository.AddTripExpenses(expenses); err != nil {
		return err
	}

	// Split expenses among users
	if err := es.SplitExpenses(expenses); err != nil {
		return err
	}

	return nil
}

func (es *expenseService) GetTripExpenses(tripID string) ([]model.TripExpense, error) {
	return es.expenseRepository.GetExpensesByTripID(tripID)
}

func (es *expenseService) GetExpensesByTripID(tripID string) ([]model.TripExpense, error) {
	return es.expenseRepository.GetExpensesByTripID(tripID)
}

func (es *expenseService) SplitExpense(expense *model.TripExpense) error {
	// Get all expense users for this trip
	expenseUsers, err := es.expenseUserRepository.GetExpenseUsersByTripID(expense.TripID)
	if err != nil {
		return err
	}

	// If no expense users found, return error
	if len(expenseUsers) == 0 {
		return errors.New("no expense users found for this trip")
	}

	// Calculate equal split amount if no split expenses provided
	if len(expense.SplitExpenses) == 0 {
		splitAmount := expense.ExpenseAmount / float64(len(expenseUsers))
		expense.SplitExpenses = make([]model.SplitExpense, 0, len(expenseUsers))

		for _, eu := range expenseUsers {
			expense.SplitExpenses = append(expense.SplitExpenses, model.SplitExpense{
				ExpenseID: expense.ExpenseID,
				UserID:    eu.UserID,
				Amount:    splitAmount,
			})
		}
	}

	// Process split expenses
	for _, split := range expense.SplitExpenses {
		// Find or create expense user record
		var expenseUser *model.ExpenseUser
		found := false

		for i := range expenseUsers {
			if expenseUsers[i].UserID == split.UserID {
				expenseUser = &expenseUsers[i]
				found = true
				break
			}
		}

		if !found {
			// Create new expense user if not found
			expenseUser = &model.ExpenseUser{
				ExpenseUserID: uuid.New().String(),
				UserID:        split.UserID,
				TripID:        expense.TripID,
				Outcome:       0,
				Income:        0,
			}
		}

		// Update outcome (what they owe)
		expenseUser.Outcome += split.Amount

		// If this user paid for the expense, update their income
		if split.UserID == expense.PaidByUserID {
			expenseUser.Income += expense.ExpenseAmount
		}

		// Save the expense user
		if found {
			if err := es.expenseUserRepository.UpdateExpenseUser(*expenseUser); err != nil {
				return err
			}
		} else {
			if err := es.expenseUserRepository.AddExpenseUsers([]model.ExpenseUser{*expenseUser}); err != nil {
				return err
			}
		}
	}

	// Handle the case where the payer is not in the split expenses
	paidByUserFound := false
	for _, split := range expense.SplitExpenses {
		if split.UserID == expense.PaidByUserID {
			paidByUserFound = true
			break
		}
	}

	if !paidByUserFound {
		// Find or create expense user record for the payer
		var paidByUser *model.ExpenseUser
		found := false

		for i := range expenseUsers {
			if expenseUsers[i].UserID == expense.PaidByUserID {
				paidByUser = &expenseUsers[i]
				found = true
				break
			}
		}

		if !found {
			// Create new expense user if not found
			paidByUser = &model.ExpenseUser{
				ExpenseUserID: uuid.New().String(),
				UserID:        expense.PaidByUserID,
				TripID:        expense.TripID,
				Outcome:       0,
				Income:        expense.ExpenseAmount,
			}

			if err := es.expenseUserRepository.AddExpenseUsers([]model.ExpenseUser{*paidByUser}); err != nil {
				return err
			}
		} else {
			paidByUser.Income += expense.ExpenseAmount

			if err := es.expenseUserRepository.UpdateExpenseUser(*paidByUser); err != nil {
				return err
			}
		}
	}

	return nil
}

func (es *expenseService) SplitExpenses(expenses []model.TripExpense) error {
	for _, expense := range expenses {
		if err := es.SplitExpense(&expense); err != nil {
			return err
		}
	}
	return nil
}

func (es *expenseService) AddExpenseUser(tripID string, userID string) error {
	// Check if user already exists as an expense user for this trip
	expenseUsers, err := es.expenseUserRepository.GetExpenseUsersByTripID(tripID)
	if err != nil {
		return err
	}

	for _, eu := range expenseUsers {
		if eu.UserID == userID {
			// User already exists as an expense user
			return nil
		}
	}

	// Create new expense user
	expenseUser := model.ExpenseUser{
		ExpenseUserID: uuid.New().String(),
		UserID:        userID,
		TripID:        tripID,
		Outcome:       0,
		Income:        0,
	}

	return es.expenseUserRepository.AddExpenseUsers([]model.ExpenseUser{expenseUser})
}

func (es *expenseService) AddExpenseUserByUsername(tripID string, username string) error {
	// Find user by username
	user, err := es.userRepository.GetByUsername(username)
	if err != nil {
		return err
	}

	// Add the user to expense users using their ID
	return es.AddExpenseUser(tripID, user.UserID)
}

func (es *expenseService) GetExpenseUsers(tripID string) ([]model.ExpenseUser, error) {
	return es.expenseUserRepository.GetExpenseUsersByTripID(tripID)
}

func (es *expenseService) CalculateBalances(tripID string) ([]dto.ExpenseBalanceDTO, error) {
	// Get all expense users for this trip
	expenseUsers, err := es.expenseUserRepository.GetExpenseUsersByTripID(tripID)
	if err != nil {
		return nil, err
	}

	// Calculate net balance for each user
	balances := make([]dto.ExpenseBalanceDTO, 0, len(expenseUsers))

	for _, eu := range expenseUsers {
		user, err := es.userRepository.GetByID(eu.UserID)
		if err != nil {
			return nil, err
		}

		netBalance := eu.Income - eu.Outcome

		balance := dto.ExpenseBalanceDTO{
			UserID:     eu.UserID,
			Username:   user.Username,
			TotalPaid:  eu.Income,
			TotalOwed:  eu.Outcome,
			NetBalance: netBalance,
		}

		balances = append(balances, balance)
	}

	// Calculate transactions to settle debts
	transactions := es.calculateTransactions(balances)

	// Assign transactions to users
	for i := range balances {
		for _, t := range transactions {
			if t.FromUserID == balances[i].UserID {
				balances[i].Transactions = append(balances[i].Transactions, t)
			}
		}
	}

	return balances, nil
}

func (es *expenseService) calculateTransactions(balances []dto.ExpenseBalanceDTO) []dto.Transaction {
	transactions := []dto.Transaction{}

	// Separate creditors (positive balance) and debtors (negative balance)
	creditors := []dto.ExpenseBalanceDTO{}
	debtors := []dto.ExpenseBalanceDTO{}

	for _, b := range balances {
		if b.NetBalance > 0 {
			creditors = append(creditors, b)
		} else if b.NetBalance < 0 {
			debtors = append(debtors, b)
		}
	}

	// Match debtors with creditors to create transactions
	for len(debtors) > 0 && len(creditors) > 0 {
		debtor := &debtors[0]
		creditor := &creditors[0]

		// Calculate transaction amount (minimum of what debtor owes and what creditor is owed)
		amount := math.Min(math.Abs(debtor.NetBalance), creditor.NetBalance)
		amount = math.Round(amount*100) / 100 // Round to 2 decimal places

		if amount > 0 {
			// Create transaction
			transaction := dto.Transaction{
				FromUserID:   debtor.UserID,
				FromUsername: debtor.Username,
				ToUserID:     creditor.UserID,
				ToUsername:   creditor.Username,
				Amount:       amount,
			}

			transactions = append(transactions, transaction)

			// Update balances
			debtor.NetBalance += amount
			creditor.NetBalance -= amount
		}

		// Remove settled accounts
		if math.Abs(debtor.NetBalance) < 0.01 {
			debtors = debtors[1:]
		}

		if math.Abs(creditor.NetBalance) < 0.01 {
			creditors = creditors[1:]
		}
	}

	return transactions
}

func (es *expenseService) GetTripExpenseSummary(tripID string, tripName string) (*dto.TripExpenseSummaryDTO, error) {
	// Get all expenses for this trip
	expenses, err := es.GetTripExpenses(tripID)
	if err != nil {
		return nil, err
	}

	// Calculate balances
	balances, err := es.CalculateBalances(tripID)
	if err != nil {
		return nil, err
	}

	// Calculate total expense
	totalExpense := 0.0
	for _, e := range expenses {
		totalExpense += e.ExpenseAmount
	}

	// Convert expenses to DTOs
	expenseDTOs := make([]dto.TripExpenseDTO, 0, len(expenses))
	for _, e := range expenses {
		expenseDTO := dto.TripExpenseDTO{
			ExpenseID:     e.ExpenseID,
			TripID:        e.TripID,
			ExpenseName:   e.ExpenseName,
			ExpenseType:   e.ExpenseType,
			ExpenseAmount: e.ExpenseAmount,
			ExpenseDate:   e.ExpenseDate,
			PaidByUserID:  e.PaidByUserID,
			PaidByUser:    e.PaidByUser,
		}

		expenseDTOs = append(expenseDTOs, expenseDTO)
	}

	// Create summary
	summary := &dto.TripExpenseSummaryDTO{
		TripID:       tripID,
		TripName:     tripName,
		TotalExpense: totalExpense,
		Expenses:     expenseDTOs,
		Balances:     balances,
	}

	return summary, nil
}
