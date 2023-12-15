
CREATE TABLE customer (
    user_id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(10) UNIQUE NOT NULL,
    rating INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);


CREATE TABLE restaurant (
    user_id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(10) UNIQUE NOT NULL,
    address VARCHAR(250) NOT NULL,
    pincode INTEGER NOT NULL,
    description VARCHAR(255),
    pure_veg boolean default TRUE,
    rating INTEGER,
    meal_type VARCHAR(10) DEFAULT 'non-veg'::varchar,
    cuisine_type TEXT[],
    is_available BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);


CREATE TABLE rider (
    user_id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(10) UNIQUE NOT NULL,
    rating INTEGER,
    is_available BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);


CREATE TABLE addresses (
    address_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    line VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(50),
    pincode VARCHAR(6),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    CONSTRAINT pk_addresses UNIQUE (address_id),
    CONSTRAINT fk_customer FOREIGN KEY (user_id) REFERENCES customer (user_id)
);
