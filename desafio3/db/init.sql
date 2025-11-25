CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);

CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);

CREATE
OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $ $ BEGIN NEW.updated_at = CURRENT_TIMESTAMP;

RETURN NEW;

END;

$ $ language 'plpgsql';

CREATE TRIGGER update_products_updated_at BEFORE
UPDATE
    ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

INSERT INTO
    products (name, description, price, stock)
VALUES
    (
        'Laptop Dell XPS 13',
        'Ultrabook com processador Intel Core i7',
        5999.00,
        10
    ),
    (
        'Mouse Logitech MX Master 3',
        'Mouse ergonômico sem fio',
        450.00,
        25
    ),
    (
        'Teclado Mecânico Keychron K2',
        'Teclado mecânico compacto RGB',
        599.00,
        15
    ),
    (
        'Monitor LG UltraWide 34"',
        'Monitor ultrawide 21:9 QHD',
        2499.00,
        8
    ),
    (
        'Headset HyperX Cloud II',
        'Headset gamer com som surround 7.1',
        599.00,
        20
    ) ON CONFLICT DO NOTHING;

DO $ $ BEGIN RAISE NOTICE 'Banco de dados inicializado com sucesso!';

RAISE NOTICE 'Total de produtos: %',
(
    SELECT
        COUNT(*)
    FROM
        products
);

END $ $;