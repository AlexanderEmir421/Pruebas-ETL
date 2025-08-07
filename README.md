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

> Extra podes crear tu propia base de datos en Supabase, generar un usuario y configurar el token en el archivo `.env` del repositorio,esto requiere la creacion de tablas dentro de supabase ya que no es posible crear tablas desde afuera.

## ⚙️ Levantar el proyecto

1. Cloná el repositorio

```bash
git clone https://github.com/tu_usuario/data-engineer-bi.git
cd data-engineer-bi
```

2. Configurá tus variables en `.env` (ver `.env`)

3. Levantá los servicios con Docker Compose

```bash
docker-compose up -d
```

Esto pondrá en marcha:
- Airflow (Web UI, Scheduler, Worker)
- PostgreSQL
- Montaje automático de DAGs en `/dags`

4.Entrar al panel de airflow `http://localhost:8080/`
-User: admin1
-password: admin1           
-#SE PUEDEN CAMBIAR EN EL .ENV

5.Activar o Ejecutar de forma manual los DAGS:
![Imagen del DAG activado programado](/src/AirflowDashboard.png)
![Imagen del DAG activar manual](/src/AirflowManual.png)

6.Los datos cargados van a la base destino en: `https://supabase.com/dashboard/project/qwpzsjaaxuijmqodvslf`

---



## 📂 Estructura del Proyecto

```

├── .Airflow/                            
│   ├── dags/                            # DAGs de Airflow (uno por ejercicio)
│   │   ├── Ej1                         
│   │   ├── Ej2
│   │   └── Ej3
│   ├── logs/                            # Crear las carpetas carpetas vacias si no las incluye el repositorio
│   ├── config/                          # Crear las carpetas carpetas vacias si no las incluye el repositorio
│   ├── plugins/                         # Crear las carpetas carpetas vacias si no las incluye el repositorio
│   └── config/                          # Crear las carpetas carpetas vacias si no las incluye el repositorio
├── Ej1/            # Scripts y documentación del ejercicio 1
│   ├── modulos
│   ├── .sql        # Este archivo tiene la consulta previamente usada para crear las tablas en supabase
│   └── README.md
├── Ej2/            # Scripts y documentación del ejercicio 2
│   ├── modulos
│   ├── .sql        # Este archivo tiene la consulta previamente usada para crear las tablas en supabase
│   └── README.md
├── Ej3/            # Scripts y documentación del ejercicio 3
│   ├── modulos
│   ├── .sql
│   └── README.md
├── src/                             #Diagramas, esquemas y recursos visuales
├── docker-compose.yml               #Define los servicios del entorno
├── Postgres                         #Creacion de usuario y db
└── README.md                        #Documentación general (este archivo)
```

---

## 📘 Documentación Técnica por Ejercicio

| Ejercicio | Descripción | Documentación |
|----------|-------------|----------------|
| Ejercicio 1 | Replicación de base PostgreSQL a Supabase | [Ver README](./Ej1/01-Ej1.md) |
| Ejercicio 2 | Ingesta incremental de cotizaciones desde API BCRA | [Ver README](./Ej2/01-Ej2.md) |
| Ejercicio 3 | Scraping de propiedades en Posadas (Misiones) | [Ver README](.) |

Cada uno de estos contiene:
- Código ETL modular
- Explicación técnica del proceso
- Automatización (Airflow DAG)
---

## 📬 Contacto

📧 [alexanderemir421@gmail.com](mailto:alexanderemir421@gmail.com)

---
