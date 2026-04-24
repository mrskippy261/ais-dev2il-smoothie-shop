import asyncio
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Create the FastAPI application
app = FastAPI(title="Kitchen Service")

# Configuration: How many cooks are available in the kitchen
NUM_COOKS = 1

# Semaphore: Controls how many smoothies can be prepared at the same time
# (one per cook). If all cooks are busy, new orders must wait.
cook_semaphore = asyncio.Semaphore(NUM_COOKS)


# Data model: Defines what a smoothie order looks like
class SmoothieOrder(BaseModel):
    flavor: str


# Endpoint: Receives requests to prepare a smoothie
@app.post("/prepare")
async def prepare_smoothie(order: SmoothieOrder):
    # Log that the request was received right as the endpoint is hit
    logger.info(f"Received order to prepare a smoothie with flavor {order.flavor}")

    try:
        # Log the debug state before waiting for the semaphore
        logger.debug(f"Waiting for a cook to become available")
        # Try to get a cook (wait max 2 seconds)
        await asyncio.wait_for(cook_semaphore.acquire(), timeout=2.0)
    except asyncio.TimeoutError:
        # Log the error if the timeout is reached before raising the HTTPException
        logger.error(f"Can't process the order: {NUM_COOKS} cooks are currently busy. Consider increasing NUM_COOKS.")
        # All cooks are busy and timeout reached -> reject the order
        raise HTTPException(status_code=503, detail="All cooks are currently busy")

    try:
        # Simulate preparing the smoothie (takes 1.5 to 2.5 seconds)
        await asyncio.sleep(random.uniform(1.5, 2.5))

        # Log the success right after the preparation time finishes
        logger.info(f"Smoothie with flavor {order.flavor} prepared")
        return {"status": "done", "flavor": order.flavor}
    finally:
        # Release the cook so they can prepare the next smoothie
        cook_semaphore.release()