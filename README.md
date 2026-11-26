# SoporteIA API

[![CI](https://github.com/Cbermudez98/soluzAi-devops/actions/workflows/ci.yml/badge.svg)](https://github.com/Cbermudez98/soluzAi-devops/actions/workflows/ci.yml)
[![Deploy GCP](https://github.com/Cbermudez98/soluzAi-devops/actions/workflows/deploy.yml/badge.svg)](https://github.com/Cbermudez98/soluzAi-devops/actions/workflows/deploy.yml)

| Enlace | Contenido |
|---|---|
| [📄 Documentación técnica](docs/DOCUMENTACION.md) | Herramientas, justificación, stages de CI y CD, evidencias |
| [⚙️ Pipeline CI](.github/workflows/ci.yml) | GitHub Actions: lint, pruebas, seguridad, build |
| [🚀 Pipeline CD](Jenkinsfile) | Jenkins: clonar, probar, build, Trivy, publicar, desplegar |
| [☸️ Manifiestos K8s](k8s/) | Deployment y Service |
| [▶️ Ejecuciones](https://github.com/Cbermudez98/soluzAi-devops/actions) | Historial de GitHub Actions |

API en **FastAPI** con arquitectura **Modelo-Vista-Controlador** que simula el servicio de agentes de SoporteIA (Unidad 3 – Laboratorio técnico CI/CD).
El agente usa reglas simples en lugar de Gemini para que las respuestas sean rápidas y deterministas durante las pruebas de carga con **k6**. Los datos viven en memoria y al iniciar se cargan dos tiendas (`tienda-demo`, `tienda-moda`) con 20 pedidos (códigos `1001`–`1020`).

## Arquitectura MVC

```
app/
├── main.py                 # Fábrica de la app: registra vistas y manejadores de errores
├── core/
│   ├── config.py           # Configuración fija de la aplicación
│   └── exceptions.py       # Errores de dominio → respuestas HTTP (404, 409, 400)
├── models/                 # MODELO: entidades y acceso a datos
│   ├── entities.py         # Store, Order, Conversation, Message, enums
│   ├── database.py         # Base de datos en memoria + datos semilla
│   └── repositories.py     # Store/Order/ConversationRepository
├── controllers/            # CONTROLADOR: reglas de negocio
│   ├── store_controller.py
│   ├── order_controller.py
│   └── chat_controller.py
├── views/                  # VISTA: rutas HTTP (routers de FastAPI)
│   ├── dependencies.py     # Inyección de controladores
│   ├── health_view.py
│   ├── store_view.py
│   ├── order_view.py
│   └── chat_view.py
├── schemas/                # Contratos de entrada/salida (Pydantic)
└── services/
    └── agent.py            # Agente simulado (detección de intención)
tests/                      # Pruebas por recurso + pruebas unitarias del agente
```

Flujo de una petición: **vista** (valida con el schema) → **controlador** (aplica reglas) → **modelo** (repositorio/datos) → el controlador devuelve la entidad → la **vista** la serializa con el schema de salida.

## Endpoints

| Método | Ruta                                   | Descripción                                  |
|--------|----------------------------------------|----------------------------------------------|
| GET    | `/`                                    | Nombre, versión y entorno del servicio       |
| GET    | `/health`                              | Health check                                 |
| GET    | `/api/v1/stores`                       | Lista tiendas                                |
| POST   | `/api/v1/stores`                       | Crea una tienda (409 si el dominio existe)   |
| GET    | `/api/v1/stores/{store_id}`            | Detalle de una tienda                        |
| GET    | `/api/v1/stores/{store_id}/orders`     | Pedidos de una tienda                        |
| POST   | `/api/v1/stores/{store_id}/orders`     | Crea un pedido                               |
| GET    | `/api/v1/orders/{order_id}`            | Detalle de un pedido                         |
| PATCH  | `/api/v1/orders/{order_id}/status`     | Cambia el estado de un pedido                |
| POST   | `/api/v1/chat`                         | Envía un mensaje al agente                   |
| GET    | `/api/v1/conversations`                | Lista conversaciones (`?store_id=&escalated=`) |
| GET    | `/api/v1/conversations/{id}`           | Historial de una conversación                |
| GET    | `/docs`                                | Swagger UI (OpenAPI integrado de FastAPI)    |
| GET    | `/redoc`                               | Documentación en ReDoc                       |
| GET    | `/openapi.json`                        | Especificación OpenAPI 3                     |

La documentación OpenAPI se genera automáticamente desde el código: metadatos y tags en `app/core/openapi.py`, y en cada vista el `summary`, la descripción (docstring), los parámetros y los errores posibles (`ErrorResponse` para 400/404/409). La prueba `tests/test_openapi.py` falla si alguna ruta queda sin documentar.

Ejemplo:

```bash
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"store_id": "tienda-demo", "message": "¿Dónde está mi pedido 1001?"}'
```

Para continuar la conversación se envía el `conversation_id` devuelto. El agente detecta las intenciones `greeting`, `faq` (horario, envío, devolución, pago), `order_status` (busca el pedido real de la tienda), `escalation` (humano, asesor, queja… marca la conversación como escalada) y `unknown`.

La aplicación no usa variables de entorno: versión, entorno, carga de datos semilla y puerto (8080) están definidos en `app/core/config.py` y en el `Dockerfile`.

## Desarrollo local (virtualenv)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8080
```

Pruebas y análisis estático:

```bash
pytest -v
ruff check .
ruff format --check .
```

Con Docker:

```bash
docker build -t soporteia-api .
docker run -p 8080:8080 soporteia-api
```

## Flujo CI/CD

```
push / PR ──► CI (GitHub Actions) ─────────► merge a main ──► CD (Jenkins)
              ├─ Análisis estático (ruff)                     1. Clonar repositorio
              ├─ Pruebas + cobertura ≥ 90 %                   2. Pruebas
              ├─ Seguridad (Gitleaks, pip-audit)              3. Construir imagen (tag = commit)
              └─ Build + smoke test + Trivy                   4. Escanear (Trivy)
                                                              5. Publicar en el registro
                                                              6. Desplegar en Kubernetes
                                                              7. Smoke test (rollback si falla)
```

- **`.github/workflows/ci.yml`**: CI en cada push o pull request a `main`.
- **`Jenkinsfile`**: CD agnóstico (registro y clúster parametrizados). Detalle de cada stage en la [documentación técnica](docs/DOCUMENTACION.md#5-pipeline-de-cd--jenkins).
- **`.github/workflows/deploy.yml`** (adicional): despliega en Cloud Run cuando el CI termina con éxito en `main` (o manualmente con *Run workflow*). Si `GCP_PROJECT_ID` no está configurado, el job se omite.

### Configuración de GCP (una sola vez)

```bash
PROJECT_ID=<tu-proyecto>
REGION=us-central1
REPO=Cbermudez98/soluzAi-devops

gcloud services enable run.googleapis.com artifactregistry.googleapis.com iamcredentials.googleapis.com --project $PROJECT_ID

# Repositorio de imágenes
gcloud artifacts repositories create soporteia --repository-format=docker --location=$REGION --project $PROJECT_ID

# Cuenta de servicio para el despliegue
gcloud iam service-accounts create github-deployer --project $PROJECT_ID
SA=github-deployer@$PROJECT_ID.iam.gserviceaccount.com
for role in roles/run.admin roles/artifactregistry.writer roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA" --role=$role
done

# Workload Identity Federation (sin llaves JSON)
gcloud iam workload-identity-pools create github --location=global --project $PROJECT_ID
gcloud iam workload-identity-pools providers create-oidc github \
  --location=global --workload-identity-pool=github --project $PROJECT_ID \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='$REPO'"

POOL=$(gcloud iam workload-identity-pools describe github --location=global --project $PROJECT_ID --format='value(name)')
gcloud iam service-accounts add-iam-policy-binding $SA --project $PROJECT_ID \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/$POOL/attribute.repository/$REPO"

# Valor para GCP_WIF_PROVIDER
gcloud iam workload-identity-pools providers describe github --location=global \
  --workload-identity-pool=github --project $PROJECT_ID --format='value(name)'
```

Luego, en GitHub → *Settings → Secrets and variables → Actions → Variables*, crear:

| Variable              | Ejemplo                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| `GCP_PROJECT_ID`      | `mi-proyecto`                                                           |
| `GCP_REGION`          | `us-central1` (opcional)                                                |
| `GAR_REPOSITORY`      | `soporteia` (opcional)                                                  |
| `CLOUD_RUN_SERVICE`   | `soporteia-api` (opcional)                                              |
| `GCP_WIF_PROVIDER`    | `projects/123456/locations/global/workloadIdentityPools/github/providers/github` |
| `GCP_SERVICE_ACCOUNT` | `github-deployer@mi-proyecto.iam.gserviceaccount.com`                   |
