"""
API Gateway — единая точка входа (порт 8000).
Маршрутизация, JWT, RBAC, rate limiting, агрегация метрик.
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth_policy import is_public_path, required_roles
from app.rate_limit import allow_request

SERVICE_NAME = "api-gateway"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "internal-service-key-2024")

SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
    "product": os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002"),
    "order": os.getenv("ORDER_SERVICE_URL", "http://localhost:8003"),
    "inventory": os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8004"),
    "picking": os.getenv("PICKING_SERVICE_URL", "http://localhost:8005"),
    "logistics": os.getenv("LOGISTICS_SERVICE_URL", "http://localhost:8006"),
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)


async def validate_token(authorization: str | None) -> dict | None:
    if not authorization:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{SERVICES['auth']}/internal/validate",
                headers={
                    "Authorization": authorization,
                    "X-Internal-Key": INTERNAL_API_KEY,
                },
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("valid"):
                    return data
    except Exception as exc:
        logger.warning("Token validation failed: %s", exc)
    return None


async def proxy_request(
    service: str,
    path: str,
    method: str,
    body: dict | None = None,
    headers: dict | None = None,
    params: dict | None = None,
    content: bytes | None = None,
):
    url = f"{SERVICES[service]}{path}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                json=body if content is None else None,
                content=content,
                headers=headers or {},
                params=params,
            )
            if response.content:
                try:
                    payload = response.json()
                except Exception:
                    payload = {"detail": response.text}
            else:
                payload = None
            return JSONResponse(content=payload, status_code=response.status_code)
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"Service {service} is unavailable")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gateway error: {exc}")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s on port %s", SERVICE_NAME, SERVICE_PORT)
    for name, url in SERVICES.items():
        logger.info("  %s -> %s", name, url)
    yield
    logger.info("Shutting down %s", SERVICE_NAME)


app = FastAPI(
    title="WMS API Gateway",
    description="Единая точка входа для микросервисов WMS",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/") or path == "/api":
        key = f"{_client_ip(request)}:{path.split('/')[2] if path.count('/') >= 2 else 'root'}"
        allowed, retry_after = allow_request(key)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Слишком много запросов. Повторите позже."},
                headers={"Retry-After": str(retry_after)},
            )
    return await call_next(request)


@app.middleware("http")
async def auth_and_rbac_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method

    if not path.startswith("/api") or is_public_path(path):
        return await call_next(request)

    authorization = request.headers.get("authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Требуется авторизация"})

    user = await validate_token(authorization)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Неверный или просроченный токен"})

    role = user.get("role") or ""
    request.state.user_id = user.get("user_id")
    request.state.user_role = role

    needed = required_roles(method, path.rstrip("/") or path)
    if needed is not None and role not in needed:
        return JSONResponse(
            status_code=403,
            content={"detail": f"Недостаточно прав. Требуется роль: {', '.join(sorted(needed))}"},
        )

    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    user_id = getattr(request.state, "user_id", None)
    logger.info(
        "[%s] %s %s -> %s (%.1f ms) user=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        user_id,
    )
    return response


@app.get("/health")
async def health():
    services_status = {}
    for name, url in SERVICES.items():
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{url}/health")
                services_status[name] = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception:
            services_status[name] = "unavailable"
    return {"status": "ok", "service": SERVICE_NAME, "services": services_status}


@app.get("/api")
def api_info():
    return {
        "name": "WMS API Gateway",
        "version": "2.0.0",
        "architecture": "Microservices",
        "features": ["routing", "jwt_auth", "rbac", "rate_limiting", "metrics_aggregation", "request_logging"],
        "services": list(SERVICES.keys()),
    }


@app.post("/api/auth/login")
async def login(request: Request):
    form = await request.body()
    headers = {"Content-Type": request.headers.get("content-type", "application/x-www-form-urlencoded")}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{SERVICES['auth']}/auth/login", content=form, headers=headers)
        return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/api/auth/me")
async def get_me(request: Request):
    return await proxy_request(
        "auth",
        "/auth/me",
        "GET",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.post("/api/auth/register")
async def register(request: Request):
    body = await request.json()
    return await proxy_request("auth", "/auth/register", "POST", body=body)


@app.post("/api/auth/refresh")
async def refresh(request: Request):
    body = await request.json()
    return await proxy_request("auth", "/auth/refresh", "POST", body=body)


@app.post("/api/auth/logout")
async def logout(request: Request):
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else None
    return await proxy_request(
        "auth",
        "/auth/logout",
        "POST",
        body=body,
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/products")
async def get_products(request: Request):
    return await proxy_request(
        "product",
        "/products",
        "GET",
        params=dict(request.query_params),
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/products/{product_id}")
async def get_product(product_id: int, request: Request):
    return await proxy_request(
        "product",
        f"/products/{product_id}",
        "GET",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.post("/api/products")
async def create_product(request: Request):
    body = await request.json()
    return await proxy_request(
        "product",
        "/products",
        "POST",
        body=body,
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int, request: Request):
    return await proxy_request(
        "product",
        f"/products/{product_id}",
        "DELETE",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/orders")
async def get_orders(request: Request):
    return await proxy_request(
        "order",
        "/orders",
        "GET",
        params=dict(request.query_params),
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.post("/api/orders")
async def create_order(request: Request):
    body = await request.json()
    return await proxy_request(
        "order",
        "/orders",
        "POST",
        body=body,
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.patch("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, request: Request):
    body: dict | None = None
    if request.headers.get("content-type", "").startswith("application/json"):
        try:
            body = await request.json()
        except Exception:
            body = None
    if not body:
        status = request.query_params.get("status")
        body = {"status": status} if status else {}
    return await proxy_request(
        "order",
        f"/orders/{order_id}/status",
        "PATCH",
        body=body,
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/inventory/warehouses")
async def inventory_warehouses(request: Request):
    return await proxy_request(
        "inventory",
        "/warehouses",
        "GET",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/inventory/zones")
async def inventory_zones(request: Request):
    return await proxy_request(
        "inventory",
        "/zones",
        "GET",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/inventory/locations")
async def inventory_locations(request: Request):
    return await proxy_request(
        "inventory",
        "/locations",
        "GET",
        params=dict(request.query_params),
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/inventory")
async def inventory_list(request: Request):
    return await proxy_request(
        "inventory",
        "/inventory",
        "GET",
        params=dict(request.query_params),
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/picking/tasks")
async def get_picking_tasks(request: Request):
    return await proxy_request(
        "picking",
        "/tasks",
        "GET",
        params=dict(request.query_params),
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/picking/tasks/{task_id}")
async def get_picking_task(task_id: int, request: Request):
    return await proxy_request(
        "picking",
        f"/tasks/{task_id}",
        "GET",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.post("/api/picking/tasks/{task_id}/start")
async def start_picking(task_id: int, request: Request):
    return await proxy_request(
        "picking",
        f"/tasks/{task_id}/start",
        "POST",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.post("/api/picking/tasks/{task_id}/complete")
async def complete_picking(task_id: int, request: Request):
    return await proxy_request(
        "picking",
        f"/tasks/{task_id}/complete",
        "POST",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/picking/stats")
async def picking_stats(request: Request):
    return await proxy_request(
        "picking",
        "/stats",
        "GET",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/logistics/shipments")
async def get_shipments(request: Request):
    return await proxy_request(
        "logistics",
        "/shipments",
        "GET",
        params=dict(request.query_params),
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.post("/api/logistics/shipments")
async def create_shipment(request: Request):
    body = await request.json()
    return await proxy_request(
        "logistics",
        "/shipments",
        "POST",
        body=body,
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/logistics/carriers")
async def get_carriers(request: Request):
    return await proxy_request(
        "logistics",
        "/carriers",
        "GET",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/logistics/stats")
async def logistics_stats(request: Request):
    return await proxy_request(
        "logistics",
        "/stats",
        "GET",
        headers={"Authorization": request.headers.get("authorization", "")},
    )


@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(request: Request):
    _ = request
    metrics = {
        "products": {"total": 0, "active": 0, "low_stock": 0},
        "orders": {"total": 0, "pending": 0, "picking": 0, "shipped": 0, "delivered_today": 0},
        "picking": {"pending_tasks": 0, "in_progress": 0, "completed_today": 0, "average_time_minutes": 0},
        "logistics": {"pending_shipments": 0, "in_transit": 0, "delivered_today": 0, "failed_deliveries": 0},
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.get(f"{SERVICES['product']}/products", params={"limit": 1000})
            if r.status_code == 200:
                products = r.json().get("data", [])
                metrics["products"]["total"] = len(products)
                metrics["products"]["active"] = len([p for p in products if p.get("stock", 0) > 0])
                metrics["products"]["low_stock"] = len([p for p in products if 0 < p.get("stock", 0) < 10])
        except Exception:
            pass
        try:
            r = await client.get(f"{SERVICES['order']}/orders", params={"limit": 1000})
            if r.status_code == 200:
                orders = r.json().get("data", [])
                metrics["orders"]["total"] = len(orders)
                metrics["orders"]["pending"] = len([o for o in orders if o.get("status") == "pending"])
                metrics["orders"]["picking"] = len([o for o in orders if o.get("status") == "picking"])
                metrics["orders"]["shipped"] = len([o for o in orders if o.get("status") == "shipped"])
        except Exception:
            pass
        try:
            r = await client.get(f"{SERVICES['picking']}/stats")
            if r.status_code == 200:
                data = r.json()
                metrics["picking"]["pending_tasks"] = data.get("pending", 0)
                metrics["picking"]["in_progress"] = data.get("in_progress", 0)
        except Exception:
            pass
    return metrics


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
