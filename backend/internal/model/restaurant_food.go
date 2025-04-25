package model

// RestaurantFood maps to the "restaurant_foods" table.
type RestaurantFood struct {
	FoodID          string  `gorm:"type:char(36);primaryKey" json:"food_id"`
	RestaurantID    string  `gorm:"type:char(36);column:restaurant_id;not null" json:"restaurant_id"`
	Name            string  `gorm:"column:name;size:100;not null" json:"name"`
	Description     string  `gorm:"column:description" json:"description"`
	FoodType        string  `gorm:"column:food_type;size:50" json:"food_type"`
	Cuisine         string  `gorm:"column:cuisine;size:100" json:"cuisine"`
	IsVegetarian    bool    `gorm:"column:is_vegetarian" json:"is_vegetarian"`
	IsVegan         bool    `gorm:"column:is_vegan" json:"is_vegan"`
	IsSpecialty     bool    `gorm:"column:is_specialty;default:false" json:"is_specialty"`
	Price           float64 `gorm:"column:price;type:decimal(10,2)" json:"price"`
	PopularityScore float64 `gorm:"column:popularity_score;type:decimal(3,1)" json:"popularity_score"`
	ImageURL        string  `gorm:"column:image_url;size:255" json:"image_url"`

	Restaurant *Restaurant `json:"restaurant,omitempty"`
}
