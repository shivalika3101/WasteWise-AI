-- =====================================================
-- Waste Classifier Database
-- Create Tables
-- =====================================================

-- ==========================================
-- Categories
-- ==========================================

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(80),
    model_label_index INTEGER NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- Bins
-- ==========================================

CREATE TABLE bins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    colour VARCHAR(20),
    description TEXT
);

-- ==========================================
-- Category ↔ Bin Mapping
-- ==========================================

CREATE TABLE category_bins (
    id SERIAL PRIMARY KEY,

    category_id INTEGER NOT NULL,

    bin_id INTEGER NOT NULL,

    is_primary BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_bin
        FOREIGN KEY (bin_id)
        REFERENCES bins(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_category_bin
        UNIQUE(category_id, bin_id)
);

-- ==========================================
-- Disposal Instructions
-- ==========================================

CREATE TABLE disposal_instructions (

    id SERIAL PRIMARY KEY,

    category_id INTEGER NOT NULL,

    instructions TEXT NOT NULL,

    notes TEXT,

    CONSTRAINT fk_instruction_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE CASCADE
);

-- ==========================================
-- Prediction History
-- ==========================================

CREATE TABLE predictions (

    id SERIAL PRIMARY KEY,

    image_ref VARCHAR(255),

    predicted_category_id INTEGER,

    confidence NUMERIC(5,4),

    chosen_bin_id INTEGER,

    is_correct BOOLEAN,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_prediction_category
        FOREIGN KEY (predicted_category_id)
        REFERENCES categories(id),

    CONSTRAINT fk_prediction_bin
        FOREIGN KEY (chosen_bin_id)
        REFERENCES bins(id)
);

CREATE INDEX ix_predictions_created_at
ON predictions(created_at);