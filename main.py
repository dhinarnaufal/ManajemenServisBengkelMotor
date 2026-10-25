from fastapi import FastAPI

from app.core.errors import register_exception_handlers
from app.routers import customers, mechanics, service_orders, spareparts, vehicles

API_PREFIX = "/api/v1"

app = FastAPI(
    title="Manajemen Servis Bengkel Motor",
    description="REST API untuk manajemen servis bengkel motor.",
    version="1.0.0",
)

register_exception_handlers(app)
for module in (customers, vehicles, mechanics, spareparts, service_orders):
    app.include_router(module.router, prefix=API_PREFIX)


@app.get("/", tags=["Info"])
def root():
    return {"service": "Manajemen Servis Bengkel Motor", "version": "1.0.0", "docs": "/docs"}
