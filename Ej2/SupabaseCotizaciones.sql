CREATE TABLE IF NOT EXISTS cotizaciones (
    fecha DATE NOT NULL,
    moneda TEXT NOT NULL,
    tipo_cambio NUMERIC(10, 4) NOT NULL,
    fuente TEXT DEFAULT 'BCRA'
);
