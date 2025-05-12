package util

import (
	"time"
)

// Common time format constants
const (
	DateFormat     = "2006-01-02"
	TimeFormat     = "15:04"
	DateTimeFormat = "2006-01-02 15:04"
)

// ParseDate parses a date string in YYYY-MM-DD format
func ParseDate(dateStr string) (time.Time, error) {
	return time.Parse(DateFormat, dateStr)
}

// ParseTime parses a time string in HH:MM format
func ParseTime(timeStr string) (time.Time, error) {
	return time.Parse(TimeFormat, timeStr)
}

// ParseDateTime parses a datetime string in YYYY-MM-DD HH:MM format
func ParseDateTime(dateTimeStr string) (time.Time, error) {
	return time.Parse(DateTimeFormat, dateTimeStr)
}

// FormatDate formats a time.Time as YYYY-MM-DD
func FormatDate(date time.Time) string {
	return date.Format(DateFormat)
}

// FormatTime formats a time.Time as HH:MM
func FormatTime(date time.Time) string {
	return date.Format(TimeFormat)
}

// FormatDateTime formats a time.Time as YYYY-MM-DD HH:MM
func FormatDateTime(date time.Time) string {
	return date.Format(DateTimeFormat)
}

// CombineDateAndTime combines a date and time into a single time.Time
func CombineDateAndTime(date time.Time, timeStr string) (*time.Time, error) {
	t, err := ParseTime(timeStr)
	if err != nil {
		return nil, err
	}
	
	combined := time.Date(
		date.Year(), date.Month(), date.Day(),
		t.Hour(), t.Minute(), 0, 0,
		time.UTC,
	)
	
	return &combined, nil
}

// GetDefaultStartDate returns the current date
func GetDefaultStartDate() time.Time {
	return time.Now().Truncate(24 * time.Hour)
}

// GetDefaultEndDate returns a date 3 days from now
func GetDefaultEndDate() time.Time {
	return time.Now().AddDate(0, 0, 2).Truncate(24 * time.Hour)
}

// TimeOfDayFromHour determines the time of day (morning, afternoon, evening) from an hour
func TimeOfDayFromHour(hour int) string {
	if hour < 12 {
		return "morning"
	} else if hour < 18 {
		return "afternoon"
	}
	return "evening"
}
