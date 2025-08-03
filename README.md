# 📊 Prueba Técnica – Data Engineer para Business Intelligence

Este repositorio tiene como objetivo construir **pipelines de replicación, scraping y actualización de datos**, desde múltiples fuentes (bases de datos, APIs, sitios web) hacia una **base de datos en la nube**, incluyendo automatización de procesos y un modelado de datos básico orientado a BI.


---

## 🧩 Objetivo General

Diseñar y automatizar pipelines de:
- Replicación de base de datos (PostgreSQL)
- Extracción incremental desde una API pública (BCRA)
- Scraping de propiedades inmobiliarias desde la web

Con destino final en una base de datos en la nube, utilizando herramientas modernas de ingeniería de datos.

---

## 🔧 Tecnologías Utilizadas

- 🐳 Docker: Contenerización de servicios
- 🐘 PostgreSQL: Base de datos origen y destino
- 🌐 Supabase: PostgreSQL gestionado en la nube
- 🐍 Python: Lenguaje principal
- 📅 Apache Airflow: Orquestador de tareas ETL
- ☁️ GitHub Actions / Render: Automatización en la nube (alternativa)
- 🛠️ Librerías: `pandas`, `requests`, `sqlalchemy`, `psycopg2`, `dotenv`, `beautifulsoup4`, `selenium`, etc.

---

## 🔐 Credenciales SUPABASE

- **Token público** de acceso para consultas:
TOKEN = <inserte_token>


- **Credenciales privadas:** solicitarlas por correo a [alexanderemir421@gmail.com](mailto:alexanderemir421@gmail.com)

> También podés crear tu propia base de datos en Supabase, generar un usuario y configurar el token en el archivo `.env` del repositorio,esto requiere la creacion de tablas dentro de supabase ya que no es posible crear tablas desde afuera.

## ⚙️ Levantar el proyecto

1. Cloná el repositorio

```bash
git clone https://github.com/tu_usuario/data-engineer-bi.git
cd data-engineer-bi
```

2. Configurá tus variables en `.env` (ver `.env.example`)

3. Levantá los servicios con Docker Compose

```bash
docker-compose up -d
```

Esto pondrá en marcha:
- Airflow (Web UI, Scheduler, Worker)
- PostgreSQL
- Montaje automático de DAGs en `/dags`

---

## 📂 Estructura del Proyecto

```
.
├── dags/                            # DAGs de Airflow (uno por ejercicio)
│   ├── dag_replicacion.py
│   ├── dag_api_bcra.py
│   └── dag_scraping.py
├── ejercicio_1_replicacion/         # Scripts y documentación del ejercicio 1
│   ├── etl_replicacion.py
│   └── README.md
├── ejercicio_2_api_bcra/            # Scripts y documentación del ejercicio 2
│   ├── etl_bcra.py
│   └── README.md
├── ejercicio_3_scraping/            # Scripts y documentación del ejercicio 3
│   ├── scraping_inmuebles.py
│   └── README.md
├── docs/                            # Diagramas, esquemas y recursos visuales
├── docker-compose.yml               # Define los servicios del entorno
├── requirements.txt                 # Librerías requeridas
└── README.md                        # Documentación general (este archivo)
```

---

## 📘 Documentación Técnica por Ejercicio

| Ejercicio | Descripción | Documentación |
|----------|-------------|----------------|
| Ejercicio 1 | Replicación de base PostgreSQL a Supabase | [Ver README](./ejercicio_1_replicacion/README.md) |
| Ejercicio 2 | Ingesta incremental de cotizaciones desde API BCRA | [Ver README](./ejercicio_2_api_bcra/README.md) |
| Ejercicio 3 | Scraping de propiedades en Posadas (Misiones) | [Ver README](./ejercicio_3_scraping/README.md) |

Cada uno de estos contiene:
- Código ETL modular
- Explicación técnica del proceso
- Automatización (Airflow DAG)
- Resultados y/o screenshots

---

## 🖼️ Diagrama General del Proyecto

![Arquitectura General](docs/arquitectura_general.png)

> Más diagramas disponibles en la carpeta `docs/`

---

## 📬 Contacto

📧 [alexanderemir421@gmail.com](mailto:alexanderemir421@gmail.com)

---
