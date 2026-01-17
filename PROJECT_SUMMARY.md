# Project Summary: FastAPI Logging Demo with Kubernetes & Azure

## 📋 Project Overview

A production-ready FastAPI application demonstrating industry best practices for logging, containerization, and cloud deployment with:

- **Local Development:** FastAPI + Loguru with structured logging
- **Containerization:** Docker with optimized images
- **Orchestration:** Kubernetes manifests with auto-scaling
- **Log Aggregation:** Fluent Bit DaemonSet for centralized log collection
- **Cloud Integration:** Azure Log Analytics for log retention and analysis

## 📁 Project Structure

```
python-logging-demo/
├── app/                          # FastAPI application
│   ├── main.py                  # Application entry point
│   ├── api/routes.py            # API endpoints
│   ├── core/                    # Core utilities
│   │   ├── logging.py           # Loguru configuration
│   │   ├── config.py            # App configuration
│   │   └── middleware.py        # Request logging middleware
│   └── models/schemas.py        # Pydantic models
├── k8s/                          # Kubernetes manifests
│   ├── namespace.yaml           # Namespace definition
│   ├── fastapi-*.yaml           # FastAPI deployment files
│   ├── fluent-bit-*.yaml        # Fluent Bit setup files
│   ├── deploy.sh                # Deployment automation script
│   └── setup-azure.sh           # Azure setup automation script
├── fluent-bit/                   # Fluent Bit configuration
│   ├── fluent-bit.conf          # Main configuration
│   ├── custom_parsers.conf      # Log parsers
│   └── setup.sh                 # Setup script
├── tests/                        # Test suite
│   └── test_api.py              # API tests
├── Dockerfile                   # Container image
├── docker-compose.yml           # Local Docker setup
├── pyproject.toml               # Poetry dependencies
└── Documentation
    ├── README.md                # Project overview
    ├── DEPLOYMENT.md            # Step-by-step deployment guide
    ├── KUBERNETES.md            # K8s deployment details
    ├── FLUENT_BIT.md            # Fluent Bit configuration
    ├── AZURE.md                 # Azure Log Analytics setup
    └── LOGGING.md               # Logging configuration
```

## 🚀 Key Features Implemented

### 1. **Application Layer**
- ✅ FastAPI with async endpoints
- ✅ Pydantic request/response validation
- ✅ Comprehensive error handling
- ✅ Health check endpoint
- ✅ User management CRUD operations
- ✅ Automatic API documentation (Swagger/ReDoc)

### 2. **Logging Pipeline**
- ✅ Loguru for powerful logging
- ✅ Multiple log handlers:
  - Console (with color)
  - General log file with rotation
  - Error-only log file
  - Structured JSON logs
- ✅ Request ID tracking (UUID per request)
- ✅ Middleware for request/response logging
- ✅ Performance metrics (response time)
- ✅ Backtrace and diagnose enabled

### 3. **Containerization**
- ✅ Multi-stage Docker build
- ✅ Optimized image size
- ✅ Health checks
- ✅ Docker Compose for local development
- ✅ Volume mounts for logs

### 4. **Kubernetes Deployment**
- ✅ Namespace isolation
- ✅ Deployment with 3 replicas
- ✅ LoadBalancer service
- ✅ ConfigMap for configuration
- ✅ Horizontal Pod Autoscaler (3-10 replicas)
- ✅ Pod Disruption Budget (min 2 available)
- ✅ Liveness and readiness probes
- ✅ Resource limits and requests
- ✅ Pod anti-affinity for distribution

### 5. **Fluent Bit Integration**
- ✅ DaemonSet on all nodes
- ✅ Container log collection
- ✅ JSON log parsing
- ✅ Kubernetes metadata enrichment:
  - Pod name, namespace
  - Labels and annotations
  - Container and cluster info
- ✅ Custom field addition (cluster, environment)
- ✅ Azure Log Analytics output
- ✅ RBAC permissions configured

### 6. **Azure Log Analytics**
- ✅ Workspace setup automation
- ✅ Credentials management
- ✅ Custom log table (FastAPILogs)
- ✅ Log retention policies
- ✅ KQL query examples
- ✅ Alert configuration examples

### 7. **Testing & Quality**
- ✅ Pytest test suite (8 tests)
- ✅ 100% API endpoint coverage
- ✅ Async test support
- ✅ Request validation testing
- ✅ Error handling tests

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Project overview, local setup, and API documentation |
| **DEPLOYMENT.md** | Complete step-by-step deployment guide |
| **KUBERNETES.md** | K8s manifests, scaling, updates, troubleshooting |
| **FLUENT_BIT.md** | Log aggregation, configuration, monitoring |
| **AZURE.md** | Log Analytics setup, KQL queries, alerts |
| **LOGGING.md** | Logging architecture, configuration details |

## 🛠️ Technology Stack

### Development
- Python 3.9+
- FastAPI 0.104.1
- Uvicorn (ASGI server)
- Poetry (dependency management)
- Pytest (testing)

### Logging
- Loguru (logging framework)
- Python JSON Logger (JSON formatting)
- Structlog (structured logging - optional)

### Containerization
- Docker
- Docker Compose

### Orchestration
- Kubernetes 1.24+
- Helm (optional)

### Cloud
- Azure Kubernetes Service (AKS)
- Azure Log Analytics
- Azure Container Registry (ACR)

## 🔧 Quick Start Commands

### Local Development
```bash
# Install and run
poetry install
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest tests/ -v

# View logs
tail -f logs/app.log
```

### Docker
```bash
# Build
docker build -t fastapi-logging-demo:v1.0 .

# Run locally
docker-compose up

# Push to registry
docker push <registry>/fastapi-logging-demo:v1.0
```

### Kubernetes
```bash
# Deploy (automated)
./k8s/deploy.sh

# Deploy (manual)
kubectl apply -f k8s/

# Setup Azure
./k8s/setup-azure.sh

# Verify
kubectl get pods -n fastapi-app
```

## 📊 Log Flow

```
Application → Loguru (console + files)
             ↓
Container logs → /var/log/containers/
             ↓
Fluent Bit (DaemonSet) → Reads, parses, enriches
             ↓
Azure Log Analytics → Storage, indexing, analysis
             ↓
KQL Queries → Dashboards, alerts, monitoring
```

## 🔍 Key API Endpoints

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `POST /api/users` - Create user
- `GET /api/users` - List users
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation

## 📈 Scaling & High Availability

### Horizontal Pod Autoscaler (HPA)
- Min replicas: 3
- Max replicas: 10
- CPU threshold: 70%
- Memory threshold: 80%

### Pod Disruption Budget (PDB)
- Minimum available: 2 pods
- Allows rolling updates with zero downtime

### Pod Anti-Affinity
- Prefers spreading pods across different nodes
- Improves availability and fault tolerance

## 🔒 Security Features

- Non-privileged container (optional)
- Read-only root filesystem (configurable)
- RBAC for Fluent Bit (minimum required permissions)
- Network policies (example provided)
- Private registry support
- Kubernetes secrets for sensitive data

## 📝 Log Sample

### Console Output
```
2024-01-17 10:30:45.123 | INFO     | app.core.middleware:dispatch:24 - Incoming request
method=GET path=/api/health query_params={} client=127.0.0.1
```

### Structured JSON
```json
{
  "timestamp": "2024-01-17T10:30:45.123456",
  "level": "INFO",
  "logger": "app.core.middleware",
  "function": "dispatch",
  "line": 24,
  "message": "Incoming request",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "GET",
  "path": "/api/health",
  "query_params": {},
  "client": "127.0.0.1"
}
```

## 🎯 Use Cases

1. **Development** - Rapid prototyping with detailed local logs
2. **Testing** - Comprehensive test suite with logging validation
3. **Staging** - Docker Compose for environment parity
4. **Production** - Full Kubernetes deployment with log aggregation
5. **Analytics** - KQL queries for insights and monitoring
6. **Compliance** - Centralized log retention with Azure

## 📦 What's Included

- ✅ Complete source code
- ✅ Docker configuration
- ✅ Kubernetes manifests
- ✅ Fluent Bit setup
- ✅ Azure integration
- ✅ Automated deployment scripts
- ✅ Comprehensive documentation
- ✅ Test suite (8 tests)
- ✅ Configuration examples
- ✅ Poetry dependencies

## 🚦 Getting Started

### 1. Read Documentation
- Start with [README.md](README.md)
- Review [DEPLOYMENT.md](DEPLOYMENT.md)

### 2. Local Development
```bash
poetry install
poetry run pytest tests/
poetry run uvicorn app.main:app --reload
```

### 3. Containerization
```bash
docker build -t fastapi-logging-demo:v1.0 .
docker-compose up
```

### 4. Kubernetes Deployment
```bash
./k8s/deploy.sh
kubectl get pods -n fastapi-app
```

### 5. Azure Setup
```bash
./k8s/setup-azure.sh
# Query logs in Azure Portal
```

## 🤝 Next Steps

Extend this project with:
- [ ] Database integration (PostgreSQL, MongoDB)
- [ ] Authentication (JWT, OAuth2)
- [ ] API rate limiting
- [ ] Webhook logging
- [ ] Metrics collection (Prometheus)
- [ ] Tracing integration (Jaeger)
- [ ] Service mesh (Istio)
- [ ] GitOps (ArgoCD)
- [ ] Helm charts
- [ ] CICD pipeline (GitHub Actions, Azure DevOps)

## 📞 Support & Resources

### Official Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Loguru Docs](https://loguru.readthedocs.io/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Fluent Bit Docs](https://docs.fluentbit.io/)
- [Azure Log Analytics](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/)

### Troubleshooting
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for common issues
- Review [KUBERNETES.md](KUBERNETES.md) for K8s troubleshooting
- See [AZURE.md](AZURE.md) for Azure issues

## 📄 License

This project is provided as-is for educational and reference purposes.

---

**Project Version:** 0.1.0  
**Last Updated:** January 2024  
**Python Version:** 3.9+  
**Status:** ✅ Ready for Production
