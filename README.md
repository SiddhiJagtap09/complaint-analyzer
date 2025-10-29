# Complaint Analyzer (Flask + Postgres + Docker)

## Quick start (Docker)
1. Copy the repo to your machine or unzip the provided archive.
2. Optionally update `.env` values (SECRET_KEY, DATABASE_URL) or pass envs in docker-compose.
3. Build and run (from project root):
   ```bash
   docker-compose up --build -d
   ```
4. Wait ~10 seconds for services to start, then seed the DB with the provided CSV:
   ```bash
   # run one-off seed inside the web container
   docker-compose exec web python seed_csv_to_db.py
   ```
5. Visit the app: http://localhost:8000
   Adminer (DB GUI): http://localhost:8080 (user: appuser / changeme)

## Run without Docker (venv)
1. Create virtualenv and install deps:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Export environment variables (Linux/macOS):
   ```bash
   export DATABASE_URL=postgresql+psycopg2://appuser:changeme@localhost:5432/complaintdb
   export SECRET_KEY='replace-me'
   ```
3. Run the app:
   ```bash
   python -m app.main
   ```

## Notes
- This repo is configured to use PostgreSQL (docker-compose starts one).
- SonarCloud/sonarqube settings are placeholders — add your tokens in CI secrets.
- The `seed_csv_to_db.py` uses `data/complaints.csv` (included).
