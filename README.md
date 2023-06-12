## Leisurebites Backend Application

Guidelines to setup application:

1. Download Postgres and Redis
2. Create a database in postgres
3. Run all .sql files from `sql_scripts` folder
4. Create a .env file (see sample for help)

Guidelines to run application:
```shell
# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Requirements
pip install -r requirements.txt

# Run
uvicorn app.main:app --port=8000
```

App should be running on http://localhost:8000
