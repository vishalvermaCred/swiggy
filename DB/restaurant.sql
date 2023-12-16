CREATE TABLE food_items (
    food_item_id UUID PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    meal_type VARCHAR(10) DEFAULT 'non-veg'::varchar,
    cuisine_type VARCHAR,
    description TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    rating INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);
