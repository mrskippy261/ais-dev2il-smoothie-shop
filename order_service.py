import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# 1. Initialize the logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Service")


class CustomerOrder(BaseModel):
    flavor: str


# The URL where your Kitchen Service is running
KITCHEN_SERVICE_URL = "http://localhost:8000/prepare"


@app.post("/order")
async def place_order(order: CustomerOrder):
    # Log that an order was received. INFO is perfect for standard, expected business events.
    logger.info(f"Received new customer order for a '{order.flavor}' smoothie.")

    try:
        # Log the outgoing network call. DEBUG is great here because you might
        # only want to see this level of detail when troubleshooting.
        logger.debug(f"Calling Kitchen Service at {KITCHEN_SERVICE_URL} for '{order.flavor}'...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                KITCHEN_SERVICE_URL,
                json={"flavor": order.flavor}
            )

        # Raise an exception if the kitchen returned an error (like a 503 Busy)
        response.raise_for_status()

        # Log success. INFO makes sense because an order completing is a standard milestone.
        logger.info(f"Successfully completed order for '{order.flavor}' smoothie!")
        return {"status": "success", "kitchen_response": response.json()}

    except httpx.HTTPStatusError as e:
        # Log failures returned by the kitchen. ERROR or WARNING is appropriate.
        logger.error(f"Order failed for '{order.flavor}'. Kitchen service returned status {e.response.status_code}.")
        raise HTTPException(status_code=e.response.status_code, detail="Could not complete order.")

    except httpx.RequestError as e:
        # Log network connection issues (e.g., the kitchen service is down).
        logger.error(f"Failed to connect to the Kitchen Service while processing '{order.flavor}'. Error: {e}")
        raise HTTPException(status_code=500, detail="Kitchen service is currently unreachable.")