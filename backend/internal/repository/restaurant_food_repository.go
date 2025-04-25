package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// RestaurantFoodRepository defines data access methods for the RestaurantFood entity.
type RestaurantFoodRepository interface {
	GetByID(foodID string) (model.RestaurantFood, error)
	Create(restaurantFood *model.RestaurantFood) error
	Update(restaurantFood *model.RestaurantFood) error
	Delete(foodID string) error
	GetByRestaurantID(restaurantID string) ([]model.RestaurantFood, error)
	GetAll() ([]model.RestaurantFood, error)
	GetPopularFoods(restaurantID string) ([]model.RestaurantFood, error)
	GetVegetarianFoods(restaurantID string) ([]model.RestaurantFood, error)
	GetVeganFoods(restaurantID string) ([]model.RestaurantFood, error)
}

// GormRestaurantFoodRepository implements RestaurantFoodRepository using GORM.
type GormRestaurantFoodRepository struct {
	DB *gorm.DB
}

// NewRestaurantFoodRepository returns a new GORM-based RestaurantFood repository.
func NewRestaurantFoodRepository(db *gorm.DB) RestaurantFoodRepository {
	return &GormRestaurantFoodRepository{DB: db}
}

// Create saves a new RestaurantFood record.
func (r *GormRestaurantFoodRepository) Create(restaurantFood *model.RestaurantFood) error {
	return r.DB.Create(restaurantFood).Error
}

// GetByID retrieves a RestaurantFood by its ID.
func (r *GormRestaurantFoodRepository) GetByID(foodID string) (model.RestaurantFood, error) {
	var restaurantFood model.RestaurantFood
	if err := r.DB.First(&restaurantFood, "food_id = ?", foodID).Error; err != nil {
		return model.RestaurantFood{}, err
	}
	return restaurantFood, nil
}

// Update modifies an existing RestaurantFood record.
func (r *GormRestaurantFoodRepository) Update(restaurantFood *model.RestaurantFood) error {
	return r.DB.Save(restaurantFood).Error
}

// Delete removes a RestaurantFood record by its ID.
func (r *GormRestaurantFoodRepository) Delete(foodID string) error {
	return r.DB.Delete(&model.RestaurantFood{}, foodID).Error
}

// GetByRestaurantID retrieves all RestaurantFood records associated with a specific RestaurantID.
func (r *GormRestaurantFoodRepository) GetByRestaurantID(restaurantID string) ([]model.RestaurantFood, error) {
	var restaurantFoods []model.RestaurantFood
	if err := r.DB.Where("restaurant_id = ?", restaurantID).Find(&restaurantFoods).Error; err != nil {
		return nil, err
	}
	return restaurantFoods, nil
}

// GetAll retrieves all RestaurantFood records.
func (r *GormRestaurantFoodRepository) GetAll() ([]model.RestaurantFood, error) {
	var restaurantFoods []model.RestaurantFood
	if err := r.DB.Find(&restaurantFoods).Error; err != nil {
		return nil, err
	}
	return restaurantFoods, nil
}

// GetPopularFoods retrieves popular RestaurantFood records associated with a specific RestaurantID.
func (r *GormRestaurantFoodRepository) GetPopularFoods(restaurantID string) ([]model.RestaurantFood, error) {
	var restaurantFoods []model.RestaurantFood
	if err := r.DB.Where("restaurant_id = ?", restaurantID).Order("popularity_score desc").Find(&restaurantFoods).Error; err != nil {
		return nil, err
	}
	return restaurantFoods, nil
}

// GetVegetarianFoods retrieves vegetarian RestaurantFood records associated with a specific RestaurantID.
func (r *GormRestaurantFoodRepository) GetVegetarianFoods(restaurantID string) ([]model.RestaurantFood, error) {
	var restaurantFoods []model.RestaurantFood
	if err := r.DB.Where("restaurant_id = ? AND is_vegetarian = ?", restaurantID, true).Find(&restaurantFoods).Error; err != nil {
		return nil, err
	}
	return restaurantFoods, nil
}

// GetVeganFoods retrieves vegan RestaurantFood records associated with a specific RestaurantID.
func (r *GormRestaurantFoodRepository) GetVeganFoods(restaurantID string) ([]model.RestaurantFood, error) {
	var restaurantFoods []model.RestaurantFood
	if err := r.DB.Where("restaurant_id = ? AND is_vegan = ?", restaurantID, true).Find(&restaurantFoods).Error; err != nil {
		return nil, err
	}
	return restaurantFoods, nil
}
