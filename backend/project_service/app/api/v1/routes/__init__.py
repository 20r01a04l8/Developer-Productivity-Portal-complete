"""
Route aggregator for API v1.

Why this pattern:
    main.py includes ONE router: v1_router.
    As new route modules are added (projects, auth, health),
    they are registered here — main.py never changes.
    This is the Open/Closed Principle applied to routing.
"""
from fastapi import APIRouter

# Future route modules are imported and included here:
# from app.api.v1.routes.projects import router as projects_router
# router.include_router(projects_router, prefix="/projects", tags=["Projects"])

router = APIRouter()
