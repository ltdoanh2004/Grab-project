CREATE DATABASE travel_planner;
USE travel_planner;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50)
);

CREATE TABLE user_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    trip_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
);

CREATE TABLE trips (
    trip_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    trip_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    budget DECIMAL(10,2),
    trip_status ENUM('planning', 'confirmed', 'completed', 'canceled') DEFAULT 'planning',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE destinations (
    destination_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    description TEXT,
    climate VARCHAR(50),
    best_season VARCHAR(100),
    image_url VARCHAR(255)
);

CREATE TABLE trip_destinations (
    trip_destination_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    destination_id INT NOT NULL,
    arrival_date DATE,
    departure_date DATE,
    order_num INT NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id)
);

CREATE TABLE activity_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    description TEXT
);

CREATE TABLE activities (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    destination_id INT,
    category_id INT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration INT,
    cost DECIMAL(10,2),
    image_url VARCHAR(255),
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id),
    FOREIGN KEY (category_id) REFERENCES activity_categories(category_id)
);

CREATE TABLE trip_activities (
    trip_activity_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    activity_id INT NOT NULL,
    scheduled_date DATE,
    start_time TIME,
    end_time TIME,
    notes TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id)
);

CREATE TABLE accommodations (
    accommodation_id INT AUTO_INCREMENT PRIMARY KEY,
    destination_id INT,
    name VARCHAR(100) NOT NULL,
    type ENUM('hotel', 'hostel', 'apartment', 'resort', 'other'),
    address TEXT,
	booking_link VARCHAR(100),
    star_rating DECIMAL(3,1),
    description TEXT,
    amenities TEXT,
    image_url VARCHAR(255),
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id)
);

CREATE TABLE trip_accommodations (
    trip_accommodation_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    accommodation_id INT NOT NULL,
    check_in_date DATE,
    check_out_date DATE,
    cost DECIMAL(10,2),
    notes TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE,
    FOREIGN KEY (accommodation_id) REFERENCES accommodations(accommodation_id)
);

CREATE TABLE places (
    place_id INT AUTO_INCREMENT PRIMARY KEY,
    destination_id INT,
    name VARCHAR(100) NOT NULL,
    place_type VARCHAR(50),
    description TEXT,
    address TEXT,
    entrance_fee DECIMAL(10,2),
    avg_visit_duration INT,
    opening_hours TEXT,
    popularity_score DECIMAL(3,1),
    image_url VARCHAR(255),
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id)
);

CREATE TABLE trip_places (
    trip_place_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    place_id INT NOT NULL,
    visit_date DATE,
    visit_start_time TIME,
    visit_end_time TIME,
    notes TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(place_id)
);

CREATE TABLE restaurants (
    restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
    destination_id INT,
    name VARCHAR(100) NOT NULL,
    establishment_type VARCHAR(50),
    cuisine_type VARCHAR(100),
    description TEXT,
    address TEXT,
    price_range ENUM('$', '$$', '$$$', '$$$$', '$$$$$'),
    avg_rating DECIMAL(3,1),
    opening_hours TEXT,
    image_url VARCHAR(255),
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id)
);

CREATE TABLE restaurant_foods (
    food_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    food_type VARCHAR(50),
    cuisine VARCHAR(100),
    is_vegetarian BOOLEAN,
    is_vegan BOOLEAN,
    is_specialty BOOLEAN DEFAULT FALSE,
    price DECIMAL(10,2),
    popularity_score DECIMAL(3,1),
    image_url VARCHAR(255),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) ON DELETE CASCADE
);

CREATE TABLE trip_restaurants (
    trip_restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    meal_date DATE,
    meal_time TIME,
    reservation_info VARCHAR(255),
    notes TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

CREATE TABLE ai_suggested (
    suggestion_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    suggestion_type ENUM('activity', 'place', 'restaurant') NOT NULL,
    activity_id INT NULL,
    place_id INT NULL,
    restaurant_id INT NULL,
    suggested_date DATE,
    suggested_time TIME,
    reason TEXT,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id),
    FOREIGN KEY (place_id) REFERENCES places(place_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

CREATE TABLE crawl_sources (
    source_id INT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_url VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crawled_destinations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(255),
    raw_data JSON,
    crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_id INT,
    FOREIGN KEY (source_id) REFERENCES crawl_sources(source_id)
);

CREATE TABLE crawled_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    destination_name VARCHAR(255),
    raw_data JSON,
    crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_id INT,
    FOREIGN KEY (source_id) REFERENCES crawl_sources(source_id)
);

CREATE TABLE crawled_places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    destination_name VARCHAR(255),
    raw_data JSON,
    crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_id INT,
    FOREIGN KEY (source_id) REFERENCES crawl_sources(source_id)
);

CREATE TABLE crawled_restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    destination_name VARCHAR(255),
    raw_data JSON,
    crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_id INT,
    FOREIGN KEY (source_id) REFERENCES crawl_sources(source_id)
);

CREATE TABLE crawled_accommodations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    destination_name VARCHAR(255),
    raw_data JSON,
    crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_id INT,
    FOREIGN KEY (source_id) REFERENCES crawl_sources(source_id)
);
