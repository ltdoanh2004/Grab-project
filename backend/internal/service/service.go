package service

import (
	"errors"
	"skeleton-internship-backend/internal/dto"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/repository"
)

type Service interface {
	CreateTodo(input *dto.TodoCreate) (*model.Todo, error)
	GetAllTodos() ([]model.Todo, error)
	GetTodoByID(id uint) (*model.Todo, error)
	UpdateTodo(id uint, input *dto.TodoCreate) (*model.Todo, error)
	DeleteTodo(id uint) error
}

type service struct {
	repo repository.Repository
}

func NewService(repo repository.Repository) Service {
	return &service{repo: repo}
}

func (s *service) CreateTodo(input *dto.TodoCreate) (*model.Todo, error) {
	todo := &model.Todo{
		Title:       input.Title,
		Description: input.Description,
		Status:      input.Status,
	}

	if todo.Status == "" {
		todo.Status = "pending"
	}

	err := s.repo.Create(todo)
	if err != nil {
		return nil, err
	}

	return todo, nil
}

func (s *service) GetAllTodos() ([]model.Todo, error) {
	return s.repo.FindAll()
}

func (s *service) GetTodoByID(id uint) (*model.Todo, error) {
	todo, err := s.repo.FindByID(id)
	if err != nil {
		return nil, err
	}
	return todo, nil
}

func (s *service) UpdateTodo(id uint, input *dto.TodoCreate) (*model.Todo, error) {
	todo, err := s.repo.FindByID(id)
	if err != nil {
		return nil, err
	}

	todo.Title = input.Title
	todo.Description = input.Description
	if input.Status != "" {
		todo.Status = input.Status
	}

	err = s.repo.Update(todo)
	if err != nil {
		return nil, err
	}

	return todo, nil
}

func (s *service) DeleteTodo(id uint) error {
	todo, err := s.repo.FindByID(id)
	if err != nil {
		return err
	}

	if todo == nil {
		return errors.New("todo not found")
	}

	return s.repo.Delete(id)
}
