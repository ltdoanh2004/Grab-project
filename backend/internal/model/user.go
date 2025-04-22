package model

// User stores basic information for an application user.
type User struct {
	UserID    string `gorm:"type:char(36);primaryKey" json:"user_id"`
	Username  string `gorm:"size:50;not null;unique" json:"username"`
	Email     string `gorm:"size:100;not null;unique" json:"email"`
	Password  string `gorm:"size:255;not null" json:"password"`
	FirstName string `gorm:"size:50" json:"first_name"`
	LastName  string `gorm:"size:50" json:"last_name"`

	// One-to-many relationship: User has many Trips.
	Trips []Trip `gorm:"foreignKey:UserID;references:UserID;constraint:OnUpdate:CASCADE,OnDelete:CASCADE" json:"trips,omitempty"`
}
