from fastapi import APIRouter

from app.controller.api_v1.healthcheck.api_controller import router as healthcheck_router
from app.controller.api_v1.booking.api_controller import router as booking_router
from app.controller.api_v1.experience.api_controller import router as experience_router
from app.controller.api_v1.customer.api_controller import router as customer_router
from app.controller.api_v1.category.api_controller import router as homepage_router
from app.controller.api_v1.security.api_controller import router as security_router
from app.controller.api_v1.supplier.api_controller import router as supplier_router
from app.utility.router import RequestResponseLoggingRoute

api_router = APIRouter(route_class=RequestResponseLoggingRoute)

api_router.include_router(healthcheck_router, prefix="", tags=["Health Check"])
api_router.include_router(booking_router, prefix="/booking", tags=["Booking"])
api_router.include_router(experience_router, prefix="/experience", tags=["Experience"])
api_router.include_router(customer_router, prefix="/customer", tags=["Customer"])
api_router.include_router(homepage_router, prefix="", tags=["Category"])
api_router.include_router(security_router, prefix="", tags=["Security"])
api_router.include_router(supplier_router, prefix="/supplier", tags=["Host & Artist"])
