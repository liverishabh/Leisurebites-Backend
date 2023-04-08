## Leisurebites Backend Application

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
