package service

import (
	"fmt"
	"skeleton-internship-backend/internal/model"
	"skeleton-internship-backend/internal/util"
)

func (s *insertDataService) InsertDestinationData(filePath string) error {
	records, err := util.ReadCSV(filePath)
	if err != nil {
		return err
	}

	tx := s.db.Begin()
	for _, record := range records {
		destination, err := s.mapRecordToDestination(record)
		if err != nil {
			fmt.Println(record["id"])
			tx.Rollback()
			return err
		}
		if err := tx.Create(destination).Error; err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit().Error
}

func (s *insertDataService) mapRecordToDestination(record map[string]string) (*model.Destination, error) {
	destination := &model.Destination{
		DestinationID: record["destination_id"],
		Name:          record["name"],
		City:          record["city"],
		Description:   record["description"],
		Climate:       record["climate"],
		BestSeason:    record["best_season"],
		ImageURL:      record["image_url"],
	}

	return destination, nil
}
