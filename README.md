# DocuMind — AI Document Intelligence Platform

Plataforma para analizar documentos con IA. Sube PDFs, chatea con ellos,
y deja que agentes autónomos extraigan insights automáticamente.

## Tech Stack

- **Backend**: Python, FastAPI, Celery
- **AI/ML**: LangChain, LangGraph, OpenAI, scikit-learn
- **Database**: PostgreSQL + pgvector
- **Queue**: Redis + Celery
- **Storage**: AWS S3 (MinIO en local)
- **Frontend**: React + TypeScript
- **Infra**: Docker, AWS ECS, Terraform
- **CI/CD**: GitHub Actions

## Inicio rápido

### Requisitos
- Docker Desktop
- Python 3.11+
- Node 20+

### Levantar en local
cp .env.example .env    # configura tus variables
make up                 # levanta todos los servicios
make migrate            # crea las tablas

### URLs
- Frontend:  http://localhost:3000
- API:       http://localhost:8000
- API Docs:  http://localhost:8000/docs
- MinIO UI:  http://localhost:9001

### Comandos útiles
make help    # ver todos los comandos disponibles
make logs    # ver logs en tiempo real
make test    # ejecutar tests
