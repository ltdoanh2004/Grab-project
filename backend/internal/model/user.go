package model

// User stores basic information for an application user.
type User struct {
	UserID    uint   `gorm:"primaryKey;autoIncrement" json:"user_id"`
	Username  string `gorm:"size:50;not null;unique" json:"username"`
	Email     string `gorm:"size:100;not null;unique" json:"email"`
	Password  string `gorm:"size:255;not null" json:"password"`
	FirstName string `gorm:"size:50" json:"first_name"`
	LastName  string `gorm:"size:50" json:"last_name"`
	// One-to-many relationship: a user can have many trips.
	Trips []Trip `gorm:"foreignKey:UserID;constraint:OnUpdate:CASCADE,OnDelete:CASCADE" json:"trips,omitempty"`
}
