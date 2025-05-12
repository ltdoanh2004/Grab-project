package repository

import (
	"skeleton-internship-backend/internal/model"

	"gorm.io/gorm"
)

// TripRestaurantRepository defines data access methods for the TripRestaurant entity.
type TripRestaurantRepository interface {
	GetByID(tripRestaurantID string) (model.TripRestaurant, error)
	Create(tripRestaurant *model.TripRestaurant) error
	Update(tripRestaurant *model.TripRestaurant) error
	Delete(tripRestaurantID string) error
	GetByTripID(tripID string) ([]model.TripRestaurant, error)
	GetByRestaurantID(restaurantID string) ([]model.TripRestaurant, error)
	GetAll() ([]model.TripRestaurant, error)
	GetWithAssociations(tripRestaurantID string) (model.TripRestaurant, error)
	GetAllWithAssociations() ([]model.TripRestaurant, error)
	UpdateByID(restaurantID string, updatedData map[string]interface{}) error
}

// GormTripRestaurantRepository implements TripRestaurantRepository using GORM.
type GormTripRestaurantRepository struct {
	DB *gorm.DB
}

// NewTripRestaurantRepository returns a new GORM-based TripRestaurant repository.
func NewTripRestaurantRepository(db *gorm.DB) TripRestaurantRepository {
	return &GormTripRestaurantRepository{DB: db}
}

// Create saves a new TripRestaurant record.
func (r *GormTripRestaurantRepository) Create(tripRestaurant *model.TripRestaurant) error {
	return r.DB.Create(tripRestaurant).Error
}

// GetByID retrieves a TripRestaurant by its ID.
func (r *GormTripRestaurantRepository) GetByID(tripRestaurantID string) (model.TripRestaurant, error) {
	var tripRestaurant model.TripRestaurant
	if err := r.DB.First(&tripRestaurant, "trip_restaurant_id = ?", tripRestaurantID).Error; err != nil {
		return model.TripRestaurant{}, err
	}
	return tripRestaurant, nil
}

// Update modifies an existing TripRestaurant record.
func (r *GormTripRestaurantRepository) Update(tripRestaurant *model.TripRestaurant) error {
	return r.DB.Save(tripRestaurant).Error
}

// Delete removes a TripRestaurant record by its ID.
func (r *GormTripRestaurantRepository) Delete(tripRestaurantID string) error {
	return r.DB.Where("trip_restaurant_id = ?", tripRestaurantID).Delete(&model.TripRestaurant{}).Error
}

// GetByTripID retrieves all TripRestaurant records associated with a specific TripID.
func (r *GormTripRestaurantRepository) GetByTripID(tripDestinationID string) ([]model.TripRestaurant, error) {
	var tripRestaurants []model.TripRestaurant
	if err := r.DB.Where("trip_destination_id = ?", tripDestinationID).Find(&tripRestaurants).Error; err != nil {
		return nil, err
	}
	return tripRestaurants, nil
}

// GetByRestaurantID retrieves all TripRestaurant records associated with a specific RestaurantID.
func (r *GormTripRestaurantRepository) GetByRestaurantID(restaurantID string) ([]model.TripRestaurant, error) {
	var tripRestaurants []model.TripRestaurant
	if err := r.DB.Where("restaurant_id = ?", restaurantID).Find(&tripRestaurants).Error; err != nil {
		return nil, err
	}
	return tripRestaurants, nil
}

// GetAll retrieves all TripRestaurant records.
func (r *GormTripRestaurantRepository) GetAll() ([]model.TripRestaurant, error) {
	var tripRestaurants []model.TripRestaurant
	if err := r.DB.Find(&tripRestaurants).Error; err != nil {
		return nil, err
	}
	return tripRestaurants, nil
}

// GetWithAssociations retrieves a TripRestaurant by its ID with associated records.
func (r *GormTripRestaurantRepository) GetWithAssociations(tripRestaurantID string) (model.TripRestaurant, error) {
	var tripRestaurant model.TripRestaurant
	if err := r.DB.Preload("Trip").Preload("Restaurant").First(&tripRestaurant, tripRestaurantID).Error; err != nil {
		return tripRestaurant, err
	}
	return tripRestaurant, nil
}

// GetAllWithAssociations retrieves all TripRestaurant records with associated records.
func (r *GormTripRestaurantRepository) GetAllWithAssociations() ([]model.TripRestaurant, error) {
	var tripRestaurants []model.TripRestaurant
	if err := r.DB.Preload("Trip").Preload("Restaurant").Find(&tripRestaurants).Error; err != nil {
		return nil, err
	}
	return tripRestaurants, nil
}

func (r *GormTripRestaurantRepository) UpdateByID(restaurantID string, updatedData map[string]interface{}) error {
	return r.DB.Model(&model.TripRestaurant{}).
		Where("trip_restaurant_id = ?", restaurantID).
		Updates(updatedData).Error
}
