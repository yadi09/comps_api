# app/api.py
from fastapi import APIRouter, HTTPException
from app.services.propstream import get_comps_for_address
from bot.logger import setup_logger
import traceback

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/comps")
def get_comps(address: str = None):
    if not address:
        logger.error("Address query parameter is missing")
        raise HTTPException(status_code=400, detail="Address query parameter is required")
    try:
        logger.info(f"Received request for comps of address: {address}")
        comps_data = get_comps_for_address(address)
        if comps_data is None:
            raise Exception("No data returned from comps service")
        return {"status": "success", "data": comps_data}
    except Exception as e:
        logger.error(f"Error getting comps for address {address}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Error retrieving comps data")
