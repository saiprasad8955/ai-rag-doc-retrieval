# Document Q&A Microservices

This project consists of two FastAPI services: `ingestion-service` and `query-service`.

## Setup

1. **Environment Variables**
   Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```

2. **Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On MacOS/Linux
   ```

3. **Install Dependencies**
   You can install dependencies for each service:
   ```bash
   # Ingestion Service
   pip install -r ingestion-service/requirements.txt

   # Query Service
   pip install -r query-service/requirements.txt
   ```

## Running the Services

You will need to open two terminal windows (or run in the background).

### 1. Run Ingestion Service
```bash
cd ingestion-service
python main.py
```
*Accessible at: http://localhost:8001*

### 2. Run Query Service
```bash
cd query-service
python main.py
```
*Accessible at: http://localhost:8002*

## API Documentation
Once running, you can access the interactive API docs at:
- Ingestion: [http://localhost:8001/docs](http://localhost:8001/docs)
- Query: [http://localhost:8002/docs](http://localhost:8002/docs)
