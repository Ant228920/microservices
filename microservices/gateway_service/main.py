import uvicorn
from core.config import settings
from core.metrics import metrics_endpoint
from core.middleware import GatewayMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from modules.auth.api.routes import router as auth_router
from modules.gateway.api.routes import router as gateway_router
from modules.proxy.api.routes import router as proxy_router

security = HTTPBearer()

app = FastAPI(
    title="API Gateway",
    description="Centralized API Gateway with Auth, Rate Limiting & Metrics",
    version="2.0.0",
    swagger_ui_init_oauth={},
    components={
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Gateway middleware (auth + rate limit + metrics + logging)
app.add_middleware(GatewayMiddleware)

# Роутери
app.include_router(auth_router, prefix="/api/v1")
app.include_router(gateway_router, prefix="/api/v1/composed", tags=["API Composition"])
app.include_router(proxy_router, prefix="/api/v1", tags=["Proxy / Routing"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/metrics", tags=["Observability"])
async def metrics():
    return metrics_endpoint()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)