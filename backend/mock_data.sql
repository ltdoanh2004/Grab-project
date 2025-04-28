-- Insert mock data into the users table
INSERT INTO users (user_id, username, email, password, first_name, last_name) VALUES
('a1b2c3d4e5f678901234567890abcdef', 'john_doe', 'john.doe@example.com', 'hashed_password', 'John', 'Doe'),
('b2c3d4e5f6a78901234567890abcdefa1', 'jane_smith', 'jane.smith@example.com', 'another_hashed_password', 'Jane', 'Smith'),
('c3d4e5f6a7b8901234567890abcdefa1b2', 'alice_wonder', 'alice.wonder@example.com', 'yet_another_password', 'Alice', 'Wonder'),
('d4e5f6a7b8c901234567890abcdefa1b2c3', 'bob_builder', 'bob.builder@example.com', 'building_password', 'Bob', 'Builder'),
('e5f6a7b8c9d01234567890abcdefa1b2c3d4', 'eve_engineer', 'eve.engineer@example.com', 'engineering_password', 'Eve', 'Engineer');

-- Insert mock data into the trips table
INSERT INTO trips (trip_id, user_id, trip_name, start_date, end_date, budget, trip_status) VALUES
('trip_000001', 'a1b2c3d4e5f678901234567890abcdef', 'Summer Vacation', '2024-07-01', '2024-07-15', 2000.00, 'planning'),
('trip_000002', 'b2c3d4e5f6a78901234567890abcdefa1', 'Winter Getaway', '2024-12-20', '2025-01-05', 3000.00, 'confirmed'),
('trip_000003', 'a1b2c3d4e5f678901234567890abcdef', 'Spring Break', '2025-03-10', '2025-03-20', 1500.00, 'planning'),
('trip_000004', 'c3d4e5f6a7b8901234567890abcdefa1b2', 'Autumn Adventure', '2024-09-15', '2024-09-25', 2500.00, 'planning'),
('trip_000005', 'd4e5f6a7b8c901234567890abcdefa1b2c3', 'Business Trip', '2024-06-01', '2024-06-05', 1000.00, 'completed');

-- Insert mock data into the destinations table
INSERT INTO destinations (destination_id, name, city, description, climate, best_season, image_url) VALUES
('hanoi', 'Hà Nội', 'Hà nội', 'The capital of Vietnam', 'Temperate', 'Spring', 'hanoi.jpg'),
('dest_000002', 'Tokyo', 'Tokyo', 'The capital of Japan', 'Subtropical', 'Autumn', 'tokyo.jpg'),
('dest_000003', 'New York', 'New York', 'The Big Apple', 'Temperate', 'Autumn', 'newyork.jpg'),
('dest_000004', 'Rome', 'Rome', 'The Eternal City', 'Mediterranean', 'Spring', 'rome.jpg'),
('dest_000005', 'Sydney', 'Sydney', 'The Harbour City', 'Subtropical', 'Summer', 'sydney.jpg');

-- Insert mock data into the trip_destinations table
INSERT INTO trip_destinations (trip_destination_id, trip_id, destination_id, arrival_date, departure_date, order_num) VALUES
('thanoi', 'trip_000001', 'hanoi', '2024-07-01', '2024-07-05', 1),
('tdest_000002', 'trip_000002', 'dest_000002', '2024-12-20', '2024-12-25', 1),
('tdest_000003', 'trip_000003', 'dest_000003', '2025-03-10', '2025-03-15', 1),
('tdest_000004', 'trip_000004', 'dest_000004', '2024-09-15', '2024-09-20', 1),
('tdest_000005', 'trip_000005', 'dest_000005', '2024-06-01', '2024-06-03', 1);

-- Update places insert statement with categories as string
INSERT INTO places (place_id, destination_id, name, url, address, duration, type, categories, image_urls, main_image, price, rating, description, opening_hours, reviews) VALUES
('act_000001', 'hanoi', 'Eiffel Tower', 'https://eiffel-tower.com', 'Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France', '2-3 hours', 'Landmark', '["Sightseeing", "Cultural"]', '["eiffel1.jpg", "eiffel2.jpg"]', 'eiffel_main.jpg', '€26.80', 4.7, 'Iconic iron lattice tower', '9:00 AM - 12:00 AM', '["Great view!", "Must visit"]'),
('act_000002', 'dest_000002', 'Tokyo Sushi Academy', 'https://sushiacademy.jp', '8-4-7 Ginza, Chuo, Tokyo 104-0061, Japan', '2 hours', 'School', '["Cultural"]', '["sushi1.jpg", "sushi2.jpg"]', 'sushi_main.jpg', '¥5000', 4.5, 'Sushi making school', '10:00 AM - 8:00 PM', '["Amazing experience"]'),
('act_000003', 'dest_000003', 'Central Park', 'https://centralpark.com', 'New York, NY, USA', '2-3 hours', 'Park', '["Adventure"]', '["park1.jpg", "park2.jpg"]', 'centralpark_main.jpg', 'Free', 4.8, 'Urban park in Manhattan', '6:00 AM - 1:00 AM', '["Beautiful park"]'),
('act_000004', 'dest_000004', 'Terme di Diocleziano', 'https://terme.it', 'Viale Enrico de Nicola, 79, 00185 Roma RM, Italy', '1.5 hours', 'Spa', '["Wellness"]', '["terme1.jpg", "terme2.jpg"]', 'terme_main.jpg', '€8.00', 4.6, 'Ancient Roman baths', '9:00 AM - 7:30 PM', '["Relaxing experience"]'),
('act_000005', 'dest_000005', 'Sydney Opera House', 'https://sydneyoperahouse.com', 'Bennelong Point, Sydney NSW 2000, Australia', '1 hour', 'Theater', '["Entertainment", "Cultural"]', '["opera1.jpg", "opera2.jpg"]', 'opera_main.jpg', 'Free', 4.9, 'Multi-venue performing arts centre', '9:00 AM - 5:00 PM', '["Architectural marvel"]');

-- Rename trip_activities to trip_places and update its structure
INSERT INTO trip_places (trip_place_id, trip_destination_id, place_id, scheduled_date, start_time, end_time, notes) VALUES
('tact_000001', 'thanoi', 'act_000001', '2024-07-02', '2024-07-02 10:00:00', '2024-07-02 11:00:00', 'Bring your camera'),
('tact_000002', 'tdest_000002', 'act_000002', '2024-12-21', '2024-12-21 14:00:00', '2024-12-21 16:00:00', 'Wear comfortable shoes'),
('tact_000003', 'tdest_000003', 'act_000003', '2025-03-12', '2025-03-12 11:00:00', '2025-03-12 12:30:00', 'Rent a bike near the park'),
('tact_000004', 'tdest_000004', 'act_000004', '2024-09-17', '2024-09-17 15:00:00', '2024-09-17 18:00:00', 'Book in advance'),
('tact_000005', 'tdest_000005', 'act_000005', '2024-06-02', '2024-06-02 10:30:00', '2024-06-02 11:15:00', 'Check show timings');

-- Update accommodations with images and room_types as JSON
INSERT INTO accommodations (accommodation_id, destination_id, name, link, price, tax_info, rating, location, description, city, elderly_friendly, room_info, unit, images, room_types) VALUES
('accom_000001', 'hanoi', 'Hotel Plaza Athenee', 'hotelplaza.com', 500.00, 'Tax included', 5.0, '25 Avenue Montaigne, 75008 Paris', 'Luxury hotel in Paris', 'Paris', true, '100 rooms available', 'EUR',
    '[{"url": "plaza_athenee_1.jpg", "alt": "Hotel Plaza Athenee Exterior"}, {"url": "plaza_athenee_2.jpg", "alt": "Hotel Plaza Athenee Room"}]',
    '[{"name": "Deluxe Room", "bed_type": "King", "price": "500", "taxes_and_fees": "Tax included", "occupancy": "2", "conditions": "Free cancellation 24h before check-in"}]'),
('accom_000002', 'dest_000002', 'Park Hyatt Tokyo', 'parkhyatt.com', 600.00, 'Tax: 10%', 5.0, '3-7-1-2 Nishi-Shinjuku', 'Luxury hotel in Tokyo', 'Tokyo', true, '150 rooms available', 'JPY',
    '[{"url": "park_hyatt_tokyo_1.jpg", "alt": "Park Hyatt Tokyo Exterior"}, {"url": "park_hyatt_tokyo_2.jpg", "alt": "Park Hyatt Tokyo Room"}]',
    '[{"name": "Park Suite", "bed_type": "King", "price": "1000", "taxes_and_fees": "10% tax", "occupancy": "2", "conditions": "Non-refundable"}]'),
('accom_000003', 'dest_000003', 'The Ritz-Carlton', 'ritzcarlton.com', 800.00, 'Tax: 8.875%', 5.0, '50 Central Park South', 'Luxury hotel in New York', 'New York', true, '200 rooms available', 'USD',
    '[{"url": "ritz_carlton_1.jpg", "alt": "Ritz Carlton Exterior"}]',
    '[{"name": "Executive Suite", "bed_type": "King", "price": "1200", "taxes_and_fees": "8.875% tax", "occupancy": "2-4", "conditions": "Free cancellation 72h before check-in"}]'),
('accom_000004', 'dest_000004', 'Hotel de Russie', 'hotelderussie.com', 450.00, 'Tax included', 4.8, 'Via del Babuino, 9', 'Luxury hotel in Rome', 'Rome', true, '80 rooms available', 'EUR',
    '[{"url": "hotel_de_russie_1.jpg", "alt": "Hotel de Russie Exterior"}]',
    '[{"name": "Classic Room", "bed_type": "Queen", "price": "450", "taxes_and_fees": "Tax included", "occupancy": "2", "conditions": "Free cancellation 24h before check-in"}]'),
('accom_000005', 'dest_000005', 'Park Hyatt Sydney', 'hyattsydney.com', 700.00, 'Tax: 10% GST', 4.9, '7 Hickson Road', 'Luxury hotel in Sydney', 'Sydney', true, '120 rooms available', 'AUD',
    '[{"url": "park_hyatt_sydney_1.jpg", "alt": "Park Hyatt Sydney Exterior"}]',
    '[{"name": "Harbour View Room", "bed_type": "King", "price": "700", "taxes_and_fees": "10% GST", "occupancy": "2", "conditions": "Free cancellation 24h before check-in"}]');

-- Insert mock data into the trip_accommodations table
INSERT INTO trip_accommodations (trip_accommodation_id, trip_destination_id, accommodation_id, check_in_date, check_out_date, cost, notes) VALUES
('tacc_000001', 'thanoi', 'accom_000001', '2024-07-01', '2024-07-05', 1500.00, 'Request a room with a view'),
('tacc_000002', 'tdest_000002', 'accom_000002', '2024-12-20', '2024-12-25', 2000.00, 'Confirm booking in advance'),
('tacc_000003', 'tdest_000003', 'accom_000003', '2025-03-10', '2025-03-15', 1800.00, 'Near Central Park'),
('tacc_000004', 'tdest_000004', 'accom_000004', '2024-09-15', '2024-09-20', 2200.00, 'Close to Spanish Steps'),
('tacc_000005', 'tdest_000005', 'accom_000005', '2024-06-01', '2024-06-03', 2500.00, 'Harbour view');

-- Insert mock data into the restaurants tablens table
INSERT INTO restaurants (restaurant_id, destination_id, name, establishment_type, cuisine_type, description, address, price_range, avg_rating, opening_hours, image_url) VALUES
    ('rest_000001', 'hanoi', 'Le Jules Verne', 'Fine Dining', 'French', 'Michelin-starred restaurant in the Eiffel Tower', 'Avenue Gustave Eiffel, 75007 Paris, France', '$$$$$', 4.8, '12PM-2PM, 7PM-10PM', 'jules_verne.jpg'),
    ('rest_000002', 'dest_000002', 'Sushi Saito', 'Sushi Restaurant', 'Japanese', 'One of the best sushi restaurants in the world', '1-9-15 Akasaka, Minato, Tokyo 107-0052, Japan', '$$$$$', 4.9, '11:30AM-2:30PM, 5PM-11PM', 'sushi_saito.jpg'),
    ('rest_000003', 'dest_000003', 'Per Se', 'Fine Dining', 'American', 'Three-Michelin-starred restaurant', '10 Columbus Circle, New York, NY 10019, USA', '$$$$$', 4.7, '5:30PM-10PM', 'per_se.jpg'),
    ('rest_000004', 'dest_000004', 'La Pergola', 'Fine Dining', 'Italian', 'Rome Cavalieri', 'Via Alberto Cadlolo, 101, 00136 Roma RM, Italy', '$$$$$', 4.9, '7:30PM-11:30PM', 'la_pergola.jpg'),
    ('rest_000005', 'dest_000005', 'Quay', 'Fine Dining', 'Australian', 'Quay restaurant description', 'Upper Level Overseas Passenger Terminal, The Rocks NSW 2000, Australia', '$$$$$', 4.8, '12PM-2:30PM, 6PM-10PM', 'quay.jpg');

-- Insert mock data into the restaurant_foods table
INSERT INTO restaurant_foods (food_id, restaurant_id, name, description, food_type, cuisine, is_vegetarian, is_vegan, is_specialty, price, popularity_score, image_url) VALUES
('food_000001', 'rest_000001', 'Foie Gras', 'Duck liver pate', 'Appetizer', 'French', false, false, true, 60.00, 4.6, 'foie_gras.jpg'),
('food_000002', 'rest_000002', 'Omakase', 'Chef''s choice sushi', 'Main Course', 'Japanese', false, false, true, 300.00, 4.9, 'omakase.jpg'),
('food_000003', 'rest_000003', 'Oysters and Pearls', 'Signature dish', 'Appetizer', 'American', false, false, true, 75.00, 4.7, 'oysters_and_pearls.jpg'),
('food_000004', 'rest_000004', 'Fagottelli Carbonara', 'Modern take on classic dish', 'Main Course', 'Italian', false, false, true, 90.00, 4.8, 'fagottelli_carbonara.jpg'),
('food_000005', 'rest_000005', 'Snow Egg', 'Signature dessert', 'Dessert', 'Australian', false, false, true, 45.00, 4.9, 'snow_egg.jpg');

-- Insert mock data into the trip_restaurants table
INSERT INTO trip_restaurants (trip_restaurant_id, trip_destination_id, restaurant_id, meal_date, start_time, end_time, reservation_info, notes) VALUES
('trest_000001', 'thanoi', 'rest_000001', '2024-07-03', '2024-07-03 19:00:00', '2024-07-03 21:00:00', 'Reserved under John Doe', 'Confirm reservation 24 hours prior'),
('trest_000002', 'tdest_000002', 'rest_000002', '2024-12-22', '2024-12-22 18:00:00', '2024-12-22 20:00:00', 'Reserved under Jane Smith', 'Request a private room'),
('trest_000003', 'tdest_000003', 'rest_000003', '2025-03-13', '2025-03-13 20:00:00', '2025-03-13 22:00:00', 'Reserved under Alice Wonder', 'Mention dietary restrictions'),
('trest_000004', 'tdest_000004', 'rest_000004', '2024-09-18', '2024-09-18 20:30:00', '2024-09-18 22:30:00', 'Reserved under Bob Builder', 'Anniversary dinner'),
('trest_000005', 'tdest_000005', 'rest_000005', '2024-06-02', '2024-06-02 19:30:00', '2024-06-02 21:30:00', 'Reserved under Eve Engineer', 'Business meeting');
