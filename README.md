# Electricity Monitor Project

This is a Django application for monitoring household electricity consumption.

## How to Run

1.  **Clone the repository.**

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the PostgreSQL Database:**
    In `psql`, create the database and user:
    ```sql
    CREATE DATABASE electricity_db;
    CREATE USER electricity_user WITH PASSWORD 'a_password_you_choose';
    GRANT ALL PRIVILEGES ON DATABASE electricity_db TO electricity_user;
    ```

5.  **Create your `.env` file:**
    Create a file named `.env` in the root of the project and add the following:

    ```env
    DEBUG=True
    SECRET_KEY=your-own-django-secret-key
    DB_NAME=electricity_db
    DB_USER=electricity_user
    DB_PASSWORD=a_password_you_choose
    DB_HOST=localhost
    DB_PORT=5432
    ```

6.  **Run migrations and create a user:**
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```

7.  **Run the server:**
    ```bash
    python manage.py runserver
    ```
