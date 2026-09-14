# EquipCare

EquipCare is a Django web application for managing shared university laboratory equipment. It supports equipment discovery, booking and returns, condition tracking, faults, maintenance, and equipment-utilisation reporting.

## Features

- Account registration and secure sign-in
- Student, laboratory staff, and administrator access
- Equipment catalogue with searching, filtering, condition, and availability information
- Conflict-safe equipment booking, approval, cancellation, and return logging
- Fault reporting and maintenance tracking
- Utilisation dashboard and reporting for staff
- SQLite database for local use and Docker support for consistent setup

## Requirements

Choose one of the following ways to run the application:

- Local setup: Python 3.10 or later and `pip`
- Docker setup: Docker Desktop with Docker Compose

No separate database server is required; SQLite is included with Python.

## Local setup (Windows)

1. Open PowerShell and navigate to the project folder


2. Create a virtual environment if one is not already present:

   ```powershell
   python -m venv venv
   ```

3. Activate it:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   If PowerShell prevents activation, run this once in the current window and try again:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

4. Install dependencies:

   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

5. Create or update the SQLite database:

   ```powershell
   .\venv\Scripts\python.exe manage.py makemigrations equipment
   .\venv\Scripts\python.exe manage.py migrate
   ```

6. Load sample data (recommended for first use):

   ```powershell
   .\venv\Scripts\python.exe manage.py seed_equipcare
   ```

7. Start the server:

   ```powershell
   .\venv\Scripts\python.exe manage.py runserver
   ```

8. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser. Stop the server with `Ctrl+C`.

If you do not activate the virtual environment, replace `python` in the commands above with `.\venv\Scripts\python.exe`.

## Demo accounts

After running `seed_equipcare`, use these accounts:

| Role | Username | Password | Main access |
| --- | --- | --- | --- |
| Administrator | `admin` | `admin12345` | Full Django administration, users, equipment, maintenance, and reports |
| Laboratory staff | `labstaff` | `staff12345` | Equipment, approvals, fault updates, maintenance, and reports |
| Student | `maya.student` | `student12345` | Search, booking, returns, and fault reporting |
| Student | `noah.student` | `student12345` | Search, booking, returns, and fault reporting |

The Django admin site is available at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Creating your own administrator

If you do not use the sample data, run this after migrations:

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

Follow the prompts and sign in at `/admin/`. In Django admin, select **Users** to grant a registered account **Staff status**. Staff can manage equipment, maintenance, and reports in the main app.

## Docker setup

1. Install and start Docker Desktop.
2. Open PowerShell in the project folder.
3. Build and launch the application:

   ```powershell
   docker compose up --build
   ```

4. In a second PowerShell window, load demo data:

   ```powershell
   docker compose exec equipcare python manage.py seed_equipcare
   ```

5. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

Use `Ctrl+C` to stop Docker. Start it again later with `docker compose up`.

## Useful development commands

```powershell
# Confirm the Django configuration is valid
.\venv\Scripts\python.exe manage.py check

# Run automated booking-rule tests
.\venv\Scripts\python.exe manage.py test

# Create and apply model database changes
.\venv\Scripts\python.exe manage.py makemigrations
.\venv\Scripts\python.exe manage.py migrate

# Load sample data safely; supplied records are not duplicated
.\venv\Scripts\python.exe manage.py seed_equipcare
```

## Troubleshooting

- **`python` is not recognised:** install Python from [python.org](https://www.python.org/downloads/) and select “Add Python to PATH” during installation.
- **Port 8000 is in use:** run `.\venv\Scripts\python.exe manage.py runserver 8001`, then visit `http://127.0.0.1:8001/`.
- **Database error after changing branches or pulling updates:** run `.\venv\Scripts\python.exe manage.py migrate`.
- **No sample records:** run `.\venv\Scripts\python.exe manage.py seed_equipcare`, refresh the browser, and sign in with a demo account.
- **Need a clean database:** stop the server, delete only `db.sqlite3`, then run `python manage.py migrate` and `python manage.py seed_equipcare`.

## Project structure

| Path | Purpose |
| --- | --- |
| `equipment/` | Models, forms, views, URLs, tests, and the seed command |
| `templates/` | Django HTML templates |
| `static/css/` | Application styles |
| `config/` | Django project configuration |
| `db.sqlite3` | Local SQLite database |
| `Dockerfile`, `docker-compose.yml` | Docker development setup |
