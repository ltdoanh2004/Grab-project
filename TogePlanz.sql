CREATE TABLE `users` (
  `user_id` INT PRIMARY KEY AUTO_INCREMENT,
  `username` VARCHAR(50) UNIQUE NOT NULL,
  `email` VARCHAR(100) UNIQUE NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50)
);

CREATE TABLE `user_history` (
  `history_id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `trip_id` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `trips` (
  `trip_id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `trip_name` VARCHAR(100) NOT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  `budget` DECIMAL(10,2),
  `trip_status` ENUM ('planning', 'confirmed', 'completed', 'canceled') DEFAULT 'planning',
  `created_at` TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `destinations` (
  `destination_id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `city` VARCHAR(100),
  `description` TEXT,
  `climate` VARCHAR(50),
  `best_season` VARCHAR(100),
  `image_url` VARCHAR(255)
);

CREATE TABLE `trip_destinations` (
  `trip_destination_id` INT PRIMARY KEY AUTO_INCREMENT,
  `trip_id` INT NOT NULL,
  `destination_id` INT NOT NULL,
  `arrival_date` DATE,
  `departure_date` DATE,
  `order_num` INT NOT NULL
);

CREATE TABLE `activity_categories` (
  `category_id` INT PRIMARY KEY AUTO_INCREMENT,
  `category_name` VARCHAR(50) NOT NULL,
  `description` TEXT
);

CREATE TABLE `activities` (
  `activity_id` INT PRIMARY KEY AUTO_INCREMENT,
  `destination_id` INT,
  `category_id` INT,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `place_id` INT AUTO_INCREMENT,
  `duration` INT,
  `cost` DECIMAL(10,2),
  `image_url` VARCHAR(255)
);

CREATE TABLE `places` (
  `place_id` INT PRIMARY KEY AUTO_INCREMENT,
  `destination_id` INT,
  `name` VARCHAR(100) NOT NULL,
  `place_type` VARCHAR(50),
  `description` TEXT,
  `address` TEXT,
  `entrance_fee` DECIMAL(10,2),
  `avg_visit_duration` INT,
  `opening_hours` TEXT,
  `popularity_score` DECIMAL(3,1),
  `image_url` VARCHAR(255)
);

CREATE TABLE `trip_activities` (
  `trip_activity_id` INT PRIMARY KEY AUTO_INCREMENT,
  `trip_destination_id` INT NOT NULL,
  `activity_id` INT NOT NULL,
  `scheduled_date` DATE,
  `start_time` TIME,
  `end_time` TIME,
  `notes` TEXT
);

CREATE TABLE `accommodations` (
  `accommodation_id` INT PRIMARY KEY AUTO_INCREMENT,
  `destination_id` INT,
  `name` VARCHAR(100) NOT NULL,
  `type` ENUM ('hotel', 'hostel', 'apartment', 'resort', 'other'),
  `address` TEXT,
  `booking_link` VARCHAR(100),
  `star_rating` DECIMAL(3,1),
  `description` TEXT,
  `amenities` TEXT,
  `image_url` VARCHAR(255)
);

CREATE TABLE `trip_accommodations` (
  `trip_accommodation_id` INT PRIMARY KEY AUTO_INCREMENT,
  `trip_destination_id` INT NOT NULL,
  `accommodation_id` INT NOT NULL,
  `check_in_date` DATE,
  `check_out_date` DATE,
  `cost` DECIMAL(10,2),
  `notes` TEXT
);

CREATE TABLE `restaurants` (
  `restaurant_id` INT PRIMARY KEY AUTO_INCREMENT,
  `destination_id` INT,
  `name` VARCHAR(100) NOT NULL,
  `establishment_type` VARCHAR(50),
  `cuisine_type` VARCHAR(100),
  `description` TEXT,
  `address` TEXT,
  `price_range` ENUM ('$', '$$', '$$$', '$$$$', '$$$$$'),
  `avg_rating` DECIMAL(3,1),
  `opening_hours` TEXT,
  `image_url` VARCHAR(255)
);

CREATE TABLE `restaurant_foods` (
  `food_id` INT PRIMARY KEY AUTO_INCREMENT,
  `restaurant_id` INT NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `food_type` VARCHAR(50),
  `cuisine` VARCHAR(100),
  `is_vegetarian` BOOLEAN,
  `is_vegan` BOOLEAN,
  `is_specialty` BOOLEAN DEFAULT false,
  `price` DECIMAL(10,2),
  `popularity_score` DECIMAL(3,1),
  `image_url` VARCHAR(255)
);

CREATE TABLE `trip_restaurants` (
  `trip_restaurant_id` INT PRIMARY KEY AUTO_INCREMENT,
  `trip_destination_id` INT NOT NULL,
  `restaurant_id` INT NOT NULL,
  `meal_date` DATE,
  `start_time` TIME,
  `end_time` TIME,
  `reservation_info` VARCHAR(255),
  `notes` TEXT
);

CREATE TABLE `ai_suggested` (
  `suggestion_id` INT PRIMARY KEY AUTO_INCREMENT,
  `trip_id` INT NOT NULL,
  `suggestion_type` ENUM ('activity', 'restaurant') NOT NULL,
  `activity_id` INT,
  `restaurant_id` INT,
  `suggested_date` DATE,
  `suggested_time` TIME,
  `reason` TEXT,
  `status` ENUM ('pending', 'accepted', 'rejected') DEFAULT 'pending',
  `generated_at` TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

ALTER TABLE `places` ADD FOREIGN KEY (`destination_id`) REFERENCES `destinations` (`destination_id`);

ALTER TABLE `user_history` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

ALTER TABLE `user_history` ADD FOREIGN KEY (`trip_id`) REFERENCES `trips` (`trip_id`) ON DELETE CASCADE;

ALTER TABLE `trips` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

ALTER TABLE `trip_destinations` ADD FOREIGN KEY (`trip_id`) REFERENCES `trips` (`trip_id`) ON DELETE CASCADE;

ALTER TABLE `trip_destinations` ADD FOREIGN KEY (`destination_id`) REFERENCES `destinations` (`destination_id`);

ALTER TABLE `activities` ADD FOREIGN KEY (`destination_id`) REFERENCES `destinations` (`destination_id`);

ALTER TABLE `activities` ADD FOREIGN KEY (`category_id`) REFERENCES `activity_categories` (`category_id`);

ALTER TABLE `activities` ADD FOREIGN KEY (`place_id`) REFERENCES `places` (`place_id`);

ALTER TABLE `trip_activities` ADD FOREIGN KEY (`trip_destination_id`) REFERENCES `trip_destinations` (`trip_destination_id`) ON DELETE CASCADE;

ALTER TABLE `trip_activities` ADD FOREIGN KEY (`activity_id`) REFERENCES `activities` (`activity_id`);

ALTER TABLE `accommodations` ADD FOREIGN KEY (`destination_id`) REFERENCES `destinations` (`destination_id`);

ALTER TABLE `trip_accommodations` ADD FOREIGN KEY (`trip_destination_id`) REFERENCES `trip_destinations` (`trip_destination_id`) ON DELETE CASCADE;

ALTER TABLE `trip_accommodations` ADD FOREIGN KEY (`accommodation_id`) REFERENCES `accommodations` (`accommodation_id`);

ALTER TABLE `restaurants` ADD FOREIGN KEY (`destination_id`) REFERENCES `destinations` (`destination_id`);

ALTER TABLE `restaurant_foods` ADD FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`) ON DELETE CASCADE;

ALTER TABLE `trip_restaurants` ADD FOREIGN KEY (`trip_destination_id`) REFERENCES `trip_destinations` (`trip_destination_id`) ON DELETE CASCADE;

ALTER TABLE `trip_restaurants` ADD FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`);

ALTER TABLE `ai_suggested` ADD FOREIGN KEY (`trip_id`) REFERENCES `trips` (`trip_id`) ON DELETE CASCADE;

ALTER TABLE `ai_suggested` ADD FOREIGN KEY (`activity_id`) REFERENCES `activities` (`activity_id`);

ALTER TABLE `ai_suggested` ADD FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`);
