CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    food_item_id UUID,
    restaurant_id UUID,
    customer_id UUID,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    quantity INTEGER NOT NULL DEFAULT 0,
    is_expired boolean DEFAULT false,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);


CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    customer_id UUID,
    restaurant_id UUID,
    rider_id UUID,
    total_amount DECIMAL(10, 2) NOT NULL,
    order_status VARCHAR(20),
    delivery_time TIMESTAMP WITHOUT TIME ZONE,
    cancelled_time TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);


CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id UUID REFERENCES orders(order_id),
    food_item_id UUID,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);
