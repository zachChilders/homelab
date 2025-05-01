# Bear Detector

A simple FastAPI web application with a health check endpoint and OpenAPI documentation.

## Setup

1. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Run the application:
```bash
poetry run uvicorn .main:app --reload
```

## API Documentation

Once the application is running, you can access:
- Interactive API documentation at http://localhost:3000/docs
- Alternative API documentation at http://localhost:3000/redoc

## Docker

To build and run the Docker container:

```bash
docker build -t home .
docker run -p 3000:3000 home
```

The application will be available at http://localhost:3000

## Kubernetes Secret Setup

```bash
kubectl create secret docker-registry acr-secret \
  --docker-server=homelabratory.azurecr.io \
  --docker-username=<your-acr-username> \
  --docker-password=<your-acr-password>
```
