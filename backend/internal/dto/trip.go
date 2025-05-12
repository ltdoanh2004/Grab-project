package dto

import (
	"fmt"
	"skeleton-internship-backend/internal/model"
	"sort"
	"time"
)

type TripDTO struct {
	TripID           string               `json:"trip_id"`
	UserID           string               `json:"user_id"`
	TripName         string               `json:"trip_name"`
	StartDate        time.Time            `json:"start_date"`
	EndDate          time.Time            `json:"end_date"`
	Budget           float64              `json:"budget"`
	TripStatus       string               `json:"trip_status"`
	TripDestinations []TripDestinationDTO `json:"trip_destinations"`
}

type TripDestinationDTO struct {
	TripDestinationID string     `json:"trip_destination_id"`
	TripID            string     `json:"trip_id"`
	DestinationID     string     `json:"destination_id"`
	ArrivalDate       *time.Time `json:"arrival_date,omitempty"`
	DepartureDate     *time.Time `json:"departure_date,omitempty"`
	OrderNum          int        `json:"order_num"`

	Places         []TripPlaceDTO         `json:"places,omitempty"`
	Accommodations []TripAccommodationDTO `json:"accommodations,omitempty"`
	Restaurants    []TripRestaurantDTO    `json:"restaurants,omitempty"`
}

type TripPlaceDTO struct {
	TripPlaceID       string     `json:"trip_place_id"`
	TripDestinationID string     `json:"trip_destination_id"`
	PlaceID           string     `json:"place_id"`
	Name              string     `json:"name,omitempty"`
	ScheduledDate     *time.Time `json:"scheduled_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	Notes             string     `json:"notes"`
	PriceAIEstimate   float64    `json:"price_ai_estimate"`
	Address           string     `json:"address,omitempty"`
	ImageURLs         []string   `json:"image_urls,omitempty"`
}

type TripAccommodationDTO struct {
	TripAccommodationID string     `json:"trip_accommodation_id"`
	TripDestinationID   string     `json:"trip_destination_id"`
	AccommodationID     string     `json:"accommodation_id"`
	Name                string     `json:"name,omitempty"`
	CheckInDate         *time.Time `json:"check_in_date,omitempty"`
	CheckOutDate        *time.Time `json:"check_out_date,omitempty"`
	StartTime           *time.Time `json:"start_time,omitempty"`
	EndTime             *time.Time `json:"end_time,omitempty"`
	PriceAIEstimate     float64    `json:"price_ai_estimate"`
	Notes               string     `json:"notes"`
	Address             string     `json:"address,omitempty"`
	ImageURLs           []string   `json:"image_urls,omitempty"`
}

type TripRestaurantDTO struct {
	TripRestaurantID  string     `json:"trip_restaurant_id"`
	TripDestinationID string     `json:"trip_destination_id"`
	RestaurantID      string     `json:"restaurant_id"`
	Name              string     `json:"name,omitempty"`
	MealDate          *time.Time `json:"meal_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	ReservationInfo   string     `json:"reservation_info"`
	Notes             string     `json:"notes"`
	PriceAIEstimate   float64    `json:"price_ai_estimate"`
	Address           string     `json:"address,omitempty"`
	ImageURLs         []string   `json:"image_urls,omitempty"`
}

type Service struct {
	Name string `json:"name"`
	URL  string `json:"url"`
	Type int    `json:"type"`
}

type Activity struct {
	ActivityID        string          `json:"activity_id"`
	ID                string          `json:"id"`
	Type              string          `json:"type"` // e.g., "place", "accommodation", "restaurant"
	Name              string          `json:"name"`
	StartTime         string          `json:"start_time,omitempty"` // "HH:mm" format
	EndTime           string          `json:"end_time,omitempty"`
	Description       string          `json:"description,omitempty"`
	PriceAIEstimate   float64         `json:"price_ai_estimate,omitempty"`
	Comments          []model.Comment `json:"comments,omitempty"`
	TripDestinationID string          `json:"trip_destination_id,omitempty"`
	Address           string          `json:"address,omitempty"`
	ImageURLs         []string        `json:"image_urls,omitempty"`
}

type Segment struct {
	TimeOfDay  string     `json:"time_of_day"` // e.g., "morning", "afternoon", "evening"
	Activities []Activity `json:"activities"`
}

type PlanByDay struct {
	Date      string    `json:"date"`      // "YYYY-MM-DD"
	DayTitle  string    `json:"day_title"` // e.g., "Ngày 1: Check-in & khám phá biển"
	Segments  []Segment `json:"segments"`
	DailyTips []string  `json:"daily_tips"`
}

type TripDTOByDate struct {
	TripID        string      `json:"trip_id"`
	UserID        string      `json:"user_id"`
	TripName      string      `json:"trip_name"`
	StartDate     string      `json:"start_date"` // "YYYY-MM-DD"
	EndDate       string      `json:"end_date"`   // "YYYY-MM-DD"
	DestinationID string      `json:"destination_id"`
	Status        string      `json:"status"`
	PlanByDay     []PlanByDay `json:"plan_by_day"`
}

func ConvertTripDTO(input TripDTOByDate) (TripDTO, error) {
	layoutDate := "2006-01-02"
	layoutTime := "2006-01-02 15:04"

	// Default to current date if input dates are empty
	if input.StartDate == "" {
		currentTime := time.Now()
		input.StartDate = currentTime.Format(layoutDate)
	}

	if input.EndDate == "" {
		// Default to 3 days from now if end date is empty
		endDate := time.Now().AddDate(0, 0, 2)
		input.EndDate = endDate.Format(layoutDate)
	}

	startDate, err := time.Parse(layoutDate, input.StartDate)
	if err != nil {
		return TripDTO{}, err
	}

	endDate, err := time.Parse(layoutDate, input.EndDate)
	if err != nil {
		return TripDTO{}, err
	}

	// Create a map to store destinations by their ID
	destinationsMap := make(map[string]*TripDestinationDTO)

	// Process all activities and group them by TripDestinationID
	for _, day := range input.PlanByDay {
		// Skip days with empty dates
		if day.Date == "" {
			continue
		}

		scheduledDate, err := time.Parse(layoutDate, day.Date)
		if err != nil {
			// Skip this day if date parsing fails instead of returning error
			continue
		}

		for _, segment := range day.Segments {
			for _, activity := range segment.Activities {
				var startTimePtr *time.Time
				var endTimePtr *time.Time

				if activity.StartTime != "" {
					st, err := time.Parse(layoutTime, day.Date+" "+activity.StartTime)
					if err == nil { // Only set if parsing succeeds
						startTimePtr = &st
					}
				}

				if activity.EndTime != "" {
					et, err := time.Parse(layoutTime, day.Date+" "+activity.EndTime)
					if err == nil { // Only set if parsing succeeds
						endTimePtr = &et
					}
				}

				// Determine which destination to use
				destID := input.DestinationID
				if activity.TripDestinationID != "" {
					destID = activity.TripDestinationID
				}

				// Create the destination if it doesn't exist
				if _, exists := destinationsMap[destID]; !exists {
					destinationsMap[destID] = &TripDestinationDTO{
						TripDestinationID: destID,
						TripID:            input.TripID,
						DestinationID:     input.DestinationID, // Using the same destination ID as input
						ArrivalDate:       &startDate,
						DepartureDate:     &endDate,
						OrderNum:          len(destinationsMap) + 1, // Assign order based on creation order
					}
				}

				// Get the destination to add this activity to
				dest := destinationsMap[destID]

				switch activity.Type {
				case "place":
					dest.Places = append(dest.Places, TripPlaceDTO{
						TripPlaceID:       activity.ActivityID,
						TripDestinationID: destID,
						PlaceID:           activity.ID,
						Name:              activity.Name,
						ScheduledDate:     &scheduledDate,
						StartTime:         startTimePtr,
						EndTime:           endTimePtr,
						Notes:             activity.Description,
						PriceAIEstimate:   activity.PriceAIEstimate,
						Address:           activity.Address,
						ImageURLs:         activity.ImageURLs,
					})
				case "accommodation":
					dest.Accommodations = append(dest.Accommodations, TripAccommodationDTO{
						TripAccommodationID: activity.ActivityID,
						TripDestinationID:   destID,
						AccommodationID:     activity.ID,
						Name:                activity.Name,
						CheckInDate:         &scheduledDate,
						CheckOutDate:        &scheduledDate, // Assuming CheckOutDate is the same as CheckInDate for simplicity.
						StartTime:           startTimePtr,
						EndTime:             endTimePtr,
						// If a CheckOutDate is available, parse it similarly.
						PriceAIEstimate: activity.PriceAIEstimate,
						Notes:           activity.Description,
						Address:         activity.Address,
						ImageURLs:       activity.ImageURLs,
					})
					fmt.Println("accommodation start time: ", dest.Accommodations[len(dest.Accommodations)-1].StartTime)
				case "restaurant":
					dest.Restaurants = append(dest.Restaurants, TripRestaurantDTO{
						TripRestaurantID:  activity.ActivityID,
						TripDestinationID: destID,
						RestaurantID:      activity.ID,
						Name:              activity.Name,
						MealDate:          &scheduledDate,
						StartTime:         startTimePtr,
						EndTime:           endTimePtr,
						ReservationInfo:   activity.Description,
						PriceAIEstimate:   activity.PriceAIEstimate,
						Notes:             activity.Description,
						Address:           activity.Address,
						ImageURLs:         activity.ImageURLs,
					})
				}
			}
		}
	}

	// Convert the map to a slice of destinations
	var destinations []TripDestinationDTO
	for _, dest := range destinationsMap {
		destinations = append(destinations, *dest)
	}

	return TripDTO{
		TripID:           input.TripID,
		UserID:           input.UserID,
		TripName:         input.TripName,
		StartDate:        startDate,
		EndDate:          endDate,
		TripStatus:       input.Status,
		TripDestinations: destinations,
	}, nil
}

func ConvertTripDTOByDate(input TripDTO) (TripDTOByDate, error) {
	layoutDate := "2006-01-02"
	layoutTime := "15:04"

	startDateStr := input.StartDate.Format(layoutDate)
	endDateStr := input.EndDate.Format(layoutDate)

	var destination string
	if len(input.TripDestinations) > 0 {
		destination = input.TripDestinations[0].DestinationID
	}

	// Group activities by scheduled date.
	activitiesByDate := make(map[string][]Activity)

	// Process all destinations and their activities
	for _, dest := range input.TripDestinations {
		// Process places.
		for _, p := range dest.Places {
			if p.ScheduledDate == nil {
				continue
			}
			dateStr := p.ScheduledDate.Format(layoutDate)
			act := Activity{
				ActivityID:        p.TripPlaceID,
				ID:                p.PlaceID,
				Type:              "place",
				Name:              p.Name,
				Description:       p.Notes,
				PriceAIEstimate:   p.PriceAIEstimate,
				TripDestinationID: p.TripDestinationID,
				Address:           p.Address,
			}
			if len(p.ImageURLs) > 0 {
				act.ImageURLs = p.ImageURLs
			}
			if p.StartTime != nil {
				act.StartTime = p.StartTime.Format(layoutTime)
			}
			if p.EndTime != nil {
				act.EndTime = p.EndTime.Format(layoutTime)
			}
			activitiesByDate[dateStr] = append(activitiesByDate[dateStr], act)
		}

		// Process accommodations.
		for _, a := range dest.Accommodations {
			if a.CheckInDate == nil {
				continue
			}
			dateStr := a.CheckInDate.Format(layoutDate)
			act := Activity{
				ActivityID:        a.TripAccommodationID,
				ID:                a.AccommodationID,
				Type:              "accommodation",
				Name:              a.Name,
				Description:       a.Notes,
				PriceAIEstimate:   a.PriceAIEstimate,
				TripDestinationID: a.TripDestinationID,
				Address:           a.Address,
			}
			if len(a.ImageURLs) > 0 {
				act.ImageURLs = a.ImageURLs
			}
			if a.StartTime != nil {
				act.StartTime = a.StartTime.Format(layoutTime)
			}
			if a.EndTime != nil {
				act.EndTime = a.EndTime.Format(layoutTime)
			}
			activitiesByDate[dateStr] = append(activitiesByDate[dateStr], act)
		}

		// Process restaurants.
		for _, r := range dest.Restaurants {
			if r.MealDate == nil {
				continue
			}
			dateStr := r.MealDate.Format(layoutDate)
			act := Activity{
				ActivityID:        r.TripRestaurantID,
				ID:                r.RestaurantID,
				Type:              "restaurant",
				Name:              r.Name,
				Description:       r.Notes,
				PriceAIEstimate:   r.PriceAIEstimate,
				TripDestinationID: r.TripDestinationID,
				Address:           r.Address,
			}
			if len(r.ImageURLs) > 0 {
				act.ImageURLs = r.ImageURLs
			}
			if r.StartTime != nil {
				act.StartTime = r.StartTime.Format(layoutTime)
			}
			if r.EndTime != nil {
				act.EndTime = r.EndTime.Format(layoutTime)
			}
			activitiesByDate[dateStr] = append(activitiesByDate[dateStr], act)
		}
	}

	// Create a sorted list of dates.
	var dates []string
	for d := range activitiesByDate {
		dates = append(dates, d)
	}
	sort.Strings(dates)

	// Build PlanByDay from the grouped activities.
	var planByDay []PlanByDay
	for i, d := range dates {
		// Partition activities into segments based on start time.
		segMap := map[string][]Activity{
			"morning":   {},
			"afternoon": {},
			"evening":   {},
			"default":   {},
		}

		for _, act := range activitiesByDate[d] {
			if act.EndTime != "" {
				t, err := time.Parse(layoutTime, act.EndTime)
				if err == nil {
					hour := t.Hour()
					if hour < 12 {
						segMap["morning"] = append(segMap["morning"], act)
					} else if hour < 18 {
						segMap["afternoon"] = append(segMap["afternoon"], act)
					} else {
						segMap["evening"] = append(segMap["evening"], act)
					}
					continue
				}
			}
			// If no valid start time, group under "default"
			segMap["default"] = append(segMap["default"], act)
		}

		// Build segments in a defined order.
		var segments []Segment
		orderedSegments := []string{"morning", "afternoon", "evening", "default"}
		for _, key := range orderedSegments {
			if len(segMap[key]) > 0 {
				segments = append(segments, Segment{
					TimeOfDay:  key,
					Activities: segMap[key],
				})
			}
		}

		planByDay = append(planByDay, PlanByDay{
			Date:     d,
			DayTitle: fmt.Sprintf("Ngày %d", i+1),
			Segments: segments,
		})
	}

	return TripDTOByDate{
		TripID:        input.TripID,
		UserID:        input.UserID,
		TripName:      input.TripName,
		StartDate:     startDateStr,
		EndDate:       endDateStr,
		DestinationID: destination,
		Status:        input.TripStatus,
		PlanByDay:     planByDay,
	}, nil
}
