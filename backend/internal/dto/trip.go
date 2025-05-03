package dto

import (
	"time"
)

type CreateTripPlaceRequest struct {
	TripDestinationID string     `json:"trip_destination_id"`
	PlaceID           string     `json:"place_id"`
	ScheduledDate     *time.Time `json:"scheduled_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	Notes             string     `json:"notes"`
}

type CreateTripAccommodationRequest struct {
	TripDestinationID string     `json:"trip_destination_id"`
	AccommodationID   string     `json:"accommodation_id"`
	CheckInDate       *time.Time `json:"check_in_date,omitempty"`
	CheckOutDate      *time.Time `json:"check_out_date,omitempty"`
	Cost              float64    `json:"cost"`
	Notes             string     `json:"notes"`
}

type CreateTripRestaurantRequest struct {
	TripDestinationID string     `json:"trip_destination_id"`
	RestaurantID      string     `json:"restaurant_id"`
	MealDate          *time.Time `json:"meal_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	ReservationInfo   string     `json:"reservation_info"`
	Notes             string     `json:"notes"`
}

type CreateTripDestinationRequest struct {
	TripID        string     `json:"trip_id"`
	DestinationID string     `json:"destination_id"`
	ArrivalDate   *time.Time `json:"arrival_date,omitempty"`
	DepartureDate *time.Time `json:"departure_date,omitempty"`
	OrderNum      int        `json:"order_num"`

	Places         []CreateTripPlaceRequest         `json:"places,omitempty"`
	Accommodations []CreateTripAccommodationRequest `json:"accommodations,omitempty"`
	Restaurants    []CreateTripRestaurantRequest    `json:"restaurants,omitempty"`
}

type CreateTripRequest struct {
	UserID           string                         `json:"user_id"`
	TripName         string                         `json:"trip_name"`
	StartDate        time.Time                      `json:"start_date"`
	EndDate          time.Time                      `json:"end_date"`
	Budget           float64                        `json:"budget"`
	TripStatus       string                         `json:"trip_status"`
	TripDestinations []CreateTripDestinationRequest `json:"trip_destinations"`
}

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
	ScheduledDate     *time.Time `json:"scheduled_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	Notes             string     `json:"notes"`
}

type TripAccommodationDTO struct {
	TripAccommodationID string     `json:"trip_accommodation_id"`
	TripDestinationID   string     `json:"trip_destination_id"`
	AccommodationID     string     `json:"accommodation_id"`
	CheckInDate         *time.Time `json:"check_in_date,omitempty"`
	CheckOutDate        *time.Time `json:"check_out_date,omitempty"`
	Cost                float64    `json:"cost"`
	Notes               string     `json:"notes"`
}

type TripRestaurantDTO struct {
	TripRestaurantID  string     `json:"trip_restaurant_id"`
	TripDestinationID string     `json:"trip_destination_id"`
	RestaurantID      string     `json:"restaurant_id"`
	MealDate          *time.Time `json:"meal_date,omitempty"`
	StartTime         *time.Time `json:"start_time,omitempty"`
	EndTime           *time.Time `json:"end_time,omitempty"`
	ReservationInfo   string     `json:"reservation_info"`
	Notes             string     `json:"notes"`
}

type Activity struct {
	ID              string   `json:"id"`
	Type            string   `json:"type"` // e.g., "place", "accommodation", "restaurant"
	Name            string   `json:"name"`
	StartTime       string   `json:"start_time,omitempty"` // "HH:mm" format
	EndTime         string   `json:"end_time,omitempty"`
	Description     string   `json:"description,omitempty"`
	Location        string   `json:"location,omitempty"`
	Rating          float64  `json:"rating,omitempty"`
	Price           float64  `json:"price,omitempty"`
	ImageURL        string   `json:"image_url,omitempty"`
	BookingLink     string   `json:"booking_link,omitempty"`
	RoomInfo        string   `json:"room_info,omitempty"`
	TaxInfo         string   `json:"tax_info,omitempty"`
	ElderlyFriendly bool     `json:"elderly_friendly,omitempty"`
	Categories      string   `json:"categories,omitempty"`
	Duration        string   `json:"duration,omitempty"`
	OpeningHours    string   `json:"opening_hours,omitempty"`
	Address         string   `json:"address,omitempty"`
	URL             string   `json:"url,omitempty"`
	Cuisines        string   `json:"cuisines,omitempty"`
	PriceRange      string   `json:"price_range,omitempty"`
	Phone           string   `json:"phone,omitempty"`
	Services        []string `json:"services,omitempty"`
}

type Segment struct {
	TimeOfDay  string     `json:"time_of_day"` // e.g., "morning", "afternoon", "evening"
	Activities []Activity `json:"activities"`
}

type PlanByDay struct {
	Date     string    `json:"date"`      // "YYYY-MM-DD"
	DayTitle string    `json:"day_title"` // e.g., "Ngày 1: Check-in & khám phá biển"
	Segments []Segment `json:"segments"`
}

type CreateTripRequestByDate struct {
	UserID      string      `json:"user_id"`
	TripName    string      `json:"trip_name"`
	StartDate   string      `json:"start_date"` // "YYYY-MM-DD"
	EndDate     string      `json:"end_date"`   // "YYYY-MM-DD"
	Destination string      `json:"destination"`
	PlanByDay   []PlanByDay `json:"plan_by_day"`
}

func ConvertToCreateTripRequest(input CreateTripRequestByDate) (CreateTripRequest, error) {
	layoutDate := "2006-01-02"
	layoutTime := "2006-01-02 15:04"

	startDate, err := time.Parse(layoutDate, input.StartDate)
	if err != nil {
		return CreateTripRequest{}, err
	}

	endDate, err := time.Parse(layoutDate, input.EndDate)
	if err != nil {
		return CreateTripRequest{}, err
	}

	dest := CreateTripDestinationRequest{
		TripID:        "", // Can be filled later
		DestinationID: input.Destination,
		ArrivalDate:   &startDate,
		DepartureDate: &endDate,
		OrderNum:      1,
	}

	for _, day := range input.PlanByDay {
		scheduledDate, err := time.Parse(layoutDate, day.Date)
		if err != nil {
			return CreateTripRequest{}, err
		}

		for _, segment := range day.Segments {
			for _, activity := range segment.Activities {
				var startTimePtr *time.Time
				var endTimePtr *time.Time

				if activity.StartTime != "" {
					st, err := time.Parse(layoutTime, day.Date+" "+activity.StartTime)
					if err != nil {
						return CreateTripRequest{}, err
					}
					startTimePtr = &st
				}

				if activity.EndTime != "" {
					et, err := time.Parse(layoutTime, day.Date+" "+activity.EndTime)
					if err != nil {
						return CreateTripRequest{}, err
					}
					endTimePtr = &et
				}

				switch activity.Type {
				case "place":
					dest.Places = append(dest.Places, CreateTripPlaceRequest{
						TripDestinationID: input.Destination,
						PlaceID:           activity.ID,
						ScheduledDate:     &scheduledDate,
						StartTime:         startTimePtr,
						EndTime:           endTimePtr,
						Notes:             activity.Description,
					})
				case "accommodation":
					dest.Accommodations = append(dest.Accommodations, CreateTripAccommodationRequest{
						TripDestinationID: input.Destination,
						AccommodationID:   activity.ID,
						CheckInDate:       &scheduledDate,
						// If a CheckOutDate is available, parse it similarly.
						Cost:  activity.Price,
						Notes: activity.Description,
					})
				case "restaurant":
					dest.Restaurants = append(dest.Restaurants, CreateTripRestaurantRequest{
						TripDestinationID: input.Destination,
						RestaurantID:      activity.ID,
						MealDate:          &scheduledDate,
						StartTime:         startTimePtr,
						EndTime:           endTimePtr,
						ReservationInfo:   activity.Description,
						Notes:             activity.Name,
					})
				}
			}
		}
	}

	return CreateTripRequest{
		UserID:           input.UserID,
		TripName:         input.TripName,
		StartDate:        startDate,
		EndDate:          endDate,
		Budget:           0,         // Fill if needed
		TripStatus:       "planned", // Adjust if needed
		TripDestinations: []CreateTripDestinationRequest{dest},
	}, nil
}
