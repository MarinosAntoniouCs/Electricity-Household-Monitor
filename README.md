# ⚡ Electricity Household Monitor

A full-stack Django application for monitoring and analyzing household electricity consumption. Converts raw time-series energy data into actionable insights through interactive visualizations and consumption analytics.

Built with **Django**, **PostgreSQL**, and **Kaggle API** integration for large-scale historical dataset ingestion.

---

## Features

- **Real-time consumption dashboard** — visualize electricity usage patterns across different time intervals
- **Historical data analysis** — identify trends, peak usage periods, and consumption anomalies
- **Kaggle dataset integration** — ingest large-scale historical energy datasets directly via Kaggle's API
- **PostgreSQL backend** — robust data management for time-series electricity measurements
- **Responsive UI** — clean, accessible templates for desktop and mobile viewing

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Django |
| Database | PostgreSQL |
| Data Source | Kaggle API |
| Frontend | HTML, Django Templates |
| Config | python-dotenv |

---

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- A [Kaggle account](https://www.kaggle.com/) with API credentials (for dataset import)

### 1. Clone the repository

```bash
git clone https://github.com/MarinosAntoniouCs/Electricity-Household-Monitor.git
cd Electricity-Household-Monitor
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the PostgreSQL database

In `psql`:

```sql
CREATE DATABASE electricity_db;
CREATE USER electricity_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE electricity_db TO electricity_user;
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```
DEBUG=True
SECRET_KEY=your-django-secret-key
DB_NAME=electricity_db
DB_USER=electricity_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 6. Run migrations and create an admin user

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Import Kaggle data

```bash
python import_kaggle_data.py
```

> Make sure your Kaggle API token (`~/.kaggle/kaggle.json`) is configured.

### 8. Start the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the dashboard.

---

## Project Structure

```
├── config/              # Django project settings
├── measurements/        # Core app — models, views, data processing
├── templates/           # HTML templates for the dashboard
├── static/images/       # Favicon and static assets
├── import_kaggle_data.py  # Kaggle dataset ingestion script
├── manage.py
├── requirements.txt
└── .env                 # Environment variables (not committed)
```

---

## License

This project was built for personal learning and portfolio purposes.
