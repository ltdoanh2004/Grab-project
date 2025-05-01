package database

import (
	"fmt"
	"skeleton-internship-backend/config"
	"skeleton-internship-backend/internal/model"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

func NewDB(cfg *config.Config) (*gorm.DB, error) {
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&parseTime=True&loc=Local",
		cfg.Database.User,
		cfg.Database.Password,
		cfg.Database.Host,
		cfg.Database.Port,
		cfg.Database.Name,
	)

	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	db.Migrator().DropTable(
		&model.User{},
		&model.Trip{},
		&model.Destination{},
		&model.Place{},
		&model.Accommodation{},
		&model.Restaurant{},
		&model.TripDestination{},
		&model.TripPlace{},
		&model.TripAccommodation{},
		&model.TripRestaurant{},
		&model.ChatMessage{},
	)

	db.Exec("SET FOREIGN_KEY_CHECKS = 0;")

	// Auto migrate the schema
	err = db.AutoMigrate(
		&model.User{},
		&model.Trip{},
		&model.Destination{},
		&model.Place{},
		&model.Accommodation{},
		&model.Restaurant{},
		&model.TripDestination{},
		&model.TripPlace{},
		&model.TripAccommodation{},
		&model.TripRestaurant{},
		&model.ChatMessage{},
	)
	if err != nil {
		return nil, err
	}
	db.Exec("SET FOREIGN_KEY_CHECKS = 1;")

	return db, nil
}
